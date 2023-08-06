'''
Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
License: Apache 2.0, see LICENSE for more details.

'''
import logging
import Queue
import re
import sys
import threading
from contextlib import closing

import boto
import sxclient

import s3import._patches  # noqa
from s3import.stream import ChunkedStream
from s3import.tools import (
    toutf8, positive_int, nonnegative_int, join_posix_paths
)
from s3import.exceptions import S3ImportException, handle_exceptions


logger = logging.getLogger(__name__)


class S3Importer(object):
    '''
    Imports buckets from S3 to SX. For every S3 bucket an SX volume is created
    (with the same name as the bucket, unless 'volume_prefix' is provided), and
    all keys are copied from the bucket to the volume (preserving the key names
    unless 'subdir' is provided).

    Initialization parameters:
      - volume_size -- size of every destination volume
      - volume_owner -- owner of every destination volume
      - volume_replica -- replica of every destination volume
      - sx -- sxclient.SXController object configured to access the destination
        SX Cluster
      - s3_context -- s3import.contexts.S3ConnectionContext object; if passed,
        will be used instead of any configuration files
      - volume_prefix -- optional prefix to prepend to every volume name prior
        to the volume's creation
      - subdir -- optional prefix to prepend to every object name prior to its
        creation in an SX volume.
      - volume_meta -- metadata to set for every volume upon creation
      - worker_num -- number of threads to create for copying the keys
      - stream_type -- stream interface type for accessing an S3 key; it should
        be initializable with key object provided by boto as an argument and
        provide at least the 'read' method with one parameter, defining a
        number of bytes to read from key's content
    '''

    def __init__(
            self, volume_size, volume_owner, volume_replica, sx,
            s3_context=None, volume_prefix=None, subdir=None, volume_meta=None,
            worker_num=1, stream_type=ChunkedStream):
        self.volume_size = volume_size
        self.volume_owner = volume_owner
        self.volume_replica = volume_replica
        self.volume_meta = volume_meta
        self.sx = sx
        self.stream_type = stream_type
        self.worker_num = positive_int(worker_num)
        self.volume_prefix = volume_prefix
        self.subdir = subdir

        if s3_context is not None:
            _config_backup = boto.config
            boto.config = boto.Config(do_load=False)
            s3 = boto.connect_s3(
                aws_access_key_id=s3_context.access_key_id,
                aws_secret_access_key=s3_context.secret_access_key,
                host=s3_context.host,
                port=s3_context.port,
                is_secure=s3_context.is_secure,
                validate_certs=s3_context.validate_certs)
            boto.config = _config_backup
        else:
            s3 = boto.connect_s3()
        self.s3 = s3

        # In spite of what is written in boto's documentation, SSL certificates
        # aren't verified by default in boto. The following check fixes this
        # behaviour.
        if self.s3.https_validate_certificates is None:
            self.s3.https_validate_certificates = True

        self._keyiter = iter(())
        self._iter_lock = threading.Lock()
        self._stopping_event = threading.Event()
        self._exception_queue = Queue.Queue()
        self._event_timeout = 60
        self._join_timeout = 1

    @handle_exceptions
    def import_all(self):
        '''Import all buckets from S3 to SX.'''

        buckets = self.s3.get_all_buckets()
        for bucket in buckets:
            self.import_bucket(bucket)

    @handle_exceptions
    def get_bucket_names(self):
        '''Get the list of all source bucket names.'''
        return [bucket.name for bucket in self.s3.get_all_buckets()]

    def import_bucket(self, bucket):
        '''
        Import the bucket to a volume with a default name (volume_prefix
        concatenated with bucket name).

        Argument can be either a boto.s3.bucket.Bucket object or a string
        object.
        '''

        if isinstance(bucket, basestring):
            bucket_name = toutf8(bucket)
        else:
            bucket_name = toutf8(bucket.name)

        if self.volume_prefix:
            volume_name = toutf8(self.volume_prefix) + bucket_name
        else:
            volume_name = bucket_name

        self.import_bucket_to_volume(bucket, volume_name)

    @handle_exceptions
    def import_bucket_to_volume(self, bucket, volume_name):
        '''
        Import the bucket to a volume named in 'volume_name'.

        The bucket argument can be either a boto.s3.bucket.Bucket object or a
        string object.

        Prior to creating a volume check if there will be enough available
        space on the volume.
        '''

        if isinstance(bucket, basestring):
            bucket = self.s3.get_bucket(bucket)
        volume_name = toutf8(volume_name)

        logger.info(
            "Importing bucket '%s' to volume '%s'" %
            (toutf8(bucket.name), volume_name)
        )

        self.check_quota_and_size(bucket, volume_name)
        self.create_volume(volume_name)
        self.copy_keys_parallelly(bucket, volume_name)

    def check_quota_and_size(self, bucket, volume_name):
        '''Make quota and size checks. Raise an error in case of failure.'''

        required_space = self.calculate_required_space(bucket, volume_name)
        self.check_quota(required_space, volume_name)
        self.check_size(required_space, volume_name)

    def calculate_required_space(self, bucket, volume_name):
        required_space = 0
        for key in bucket.list():
            dest = toutf8(key.name)
            if self.subdir:
                dest = join_posix_paths(toutf8(self.subdir), dest)
            if self._file_sizes_differ(key, volume_name, dest):
                required_space += key.size + len(toutf8(key.name))
        return required_space

    def check_quota(self, required_space, volume_name):
        '''
        Check if destination volume owner's remaining quota is enough to import
        the keys. If not, raise an error.
        '''

        remaining_quota = self.get_remaining_quota(volume_name)
        if remaining_quota is not None:
            if required_space > remaining_quota:
                err_msg = (
                    "Remaining quota %i of '%s' owner too small to contain "
                    "%i bytes from the source bucket." %
                    (remaining_quota, volume_name, required_space)
                )
                raise S3ImportException(err_msg)

    def get_remaining_quota(self, volume_name):
        '''
        Return the remaining quota of SX volume's designated/existing owner if
        it's set, otherwise return None.
        '''

        volume_list = self.sx.listVolumes.json_call()[u'volumeList']
        if volume_name in volume_list:
            owner = volume_list[volume_name]['owner']
        else:
            owner = self.volume_owner

        user_list = self.sx.listUsers.json_call()
        try:
            user_quota = user_list[owner]['userQuota']
            user_quota_used = user_list[owner]['userQuotaUsed']
        except KeyError:
            raise S3ImportException('%s: no such user.' % toutf8(owner))

        if not user_quota:
            remaining = None
        else:
            remaining = nonnegative_int(user_quota - user_quota_used)
        return remaining

    def check_size(self, required_space, volume_name):
        '''
        Check if there is enough available space on the destination volume to
        import the keys. If not, raise an error.
        '''

        available_space = self.get_available_space(volume_name)
        volume_size = (
            available_space if available_space is not None else
            self.volume_size
        )

        if required_space > volume_size:
            if available_space is None:
                err_msg = (
                    "Size %i of volume '%s' too small to contain %i bytes "
                    "from the source bucket." %
                    (volume_size, volume_name, required_space)
                )
            else:
                err_msg = (
                    "Not enough available space on existing volume '%s' to "
                    "contain %i bytes from the source bucket." %
                    (volume_name, required_space)
                )
            raise S3ImportException(err_msg)

    def get_available_space(self, volume_name):
        '''
        Return the amount of available space on the SX volume if it exists,
        otherwise return None.
        '''

        volume_list = self.sx.listVolumes.json_call()[u'volumeList']
        if volume_name in volume_list:
            size_bytes = volume_list[volume_name][u'sizeBytes']
            used_size = volume_list[volume_name][u'usedSize']
            size = nonnegative_int(size_bytes - used_size)
        else:
            size = None
        return size

    def create_volume(self, name):
        '''Create the SX volume if it doesn't exist yet.'''

        logger.debug(
            "Attempting to create volume '%s' in the SX cluster." % name
        )
        try:
            self.sx.createVolume.call(
                volume=name, volumeSize=self.volume_size,
                owner=self.volume_owner, replicaCount=self.volume_replica,
                volumeMeta=self.volume_meta)
            logger.debug("Volume '%s' created." % name)
        except sxclient.exceptions.SXClusterNonFatalError:
            err_val = sys.exc_info()[1]
            if re.search(
                    'volume already exists', str(err_val), re.IGNORECASE):
                log_msg = (
                    "Volume '%s' already exists. Data will be imported "
                    "to this volume." % name
                )
                logger.warning(log_msg)
            else:
                raise

    def copy_keys_parallelly(self, bucket, volume_name):
        '''
        Copy keys for a given bucket parallelly, using threads.

        At this point it is assumed that the destination volume exists and
        contains enough free space to receive the keys.
        '''

        logger.debug(
            "Attempting to copy keys from bucket '%s'." % toutf8(bucket.name)
        )
        keyiter = iter(bucket.list())

        try:
            threads = []
            for i in range(self.worker_num):
                t = threading.Thread(
                    target=self._copy_keys, args=(keyiter, volume_name)
                )
                t.start()
                threads.append(t)
                logger.debug("Thread %s started." % t.name)

            while not self._stopping_event.is_set():
                self._stopping_event.wait(self._event_timeout)
        except KeyboardInterrupt as exc:
            self._stopping_event.set()
            raise exc.__class__('Transfer terminated.')

        try:
            exc_info = self._exception_queue.get(block=False)
            raise exc_info[0], exc_info[1], exc_info[2]
        except Queue.Empty:
            pass

        while threads:
            for t in threads:
                t.join(self._join_timeout)
                if not t.is_alive():
                    threads.remove(t)
                    break

        self._stopping_event.clear()

    def _copy_keys(self, keyiter, volume_name):
        uploader = sxclient.SXFileUploader(self.sx)

        while not self._stopping_event.is_set():
            try:
                with self._iter_lock:
                    key = next(keyiter)
                self._copy_key(key, volume_name, uploader)
            except StopIteration:
                logger.debug('Key iterator exhausted.')
                self._stopping_event.set()
                break
            except BaseException:
                exc_info = sys.exc_info()
                logger.error(str(exc_info[1]))
                self._exception_queue.put(exc_info)
                self._stopping_event.set()

    def _copy_key(self, key, volume_name, uploader):
        bucket_name = toutf8(key.bucket.name)
        source_filename = toutf8(key.name)
        file_size = key.size

        dest_filename = toutf8(key.name)
        if self.subdir:
            dest_filename = join_posix_paths(
                toutf8(self.subdir), dest_filename
            )

        logger.debug(
            "Attempting to copy 's3://%(bucket)s/%(source)s' "
            "to 'sx://%(cluster)s/%(volume)s/%(dest)s'." %
            {'source': source_filename,
             'bucket': bucket_name,
             'cluster': self.sx.cluster.name,
             'volume': volume_name,
             'dest': dest_filename}
        )

        if key.version_id is not None:
            logger.warning(
                "Key '%s' is versioned; copying only the latest version" %
                toutf8(source_filename)
            )

        if self._file_sizes_differ(key, volume_name, dest_filename):
            with closing(self.stream_type(key)) as file_stream:
                uploader.upload_stream(
                    volume_name, file_size, dest_filename, file_stream)
                logger.debug(
                    "'s3://%(bucket)s/%(source)s' successfully copied "
                    "to 'sx://%(cluster)s/%(volume)s/%(dest)s'." %
                    {'source': source_filename,
                     'bucket': bucket_name,
                     'cluster': self.sx.cluster.name,
                     'volume': volume_name,
                     'dest': dest_filename}
                )
        else:
            logger.debug(
                "Source and destination of '%s' have the same size. "
                "Key will not be copied." % source_filename
            )

    def _file_sizes_differ(self, key, volume_name, dest_filename):
        try:
            response_json = self.sx.getFile.json_call(
                volume_name, dest_filename
            )
        except sxclient.exceptions.SXClusterNotFound:
            return True
        dest_size = response_json['fileSize']
        if dest_size == key.size:
            return False
        else:
            return True
