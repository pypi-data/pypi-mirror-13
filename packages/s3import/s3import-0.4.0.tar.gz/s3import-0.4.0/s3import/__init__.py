'''
Copyright (c) 2015 Skylable Ltd.
License: Apache 2.0, see LICENSE for more details.

'''
import logging

from importer import S3Importer
from contexts import S3ConnectionContext
from exceptions import S3ImportException

__version__ = '0.4.0'

__all__ = ['S3Importer', 'S3ConnectionContext', 'S3ImportException']

# Set default logging handler to avoid "No handler found" warnings.
logging.getLogger(__name__).addHandler(logging.NullHandler())
