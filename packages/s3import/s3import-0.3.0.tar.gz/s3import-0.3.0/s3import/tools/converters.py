'''
Copyright (c) 2015 Skylable Ltd.
License: Apache 2.0, see LICENSE for more details.

'''
import re

__all__ = ['humansize_int', 'positive_int', 'nonnegative_int']


SUFFIX_TO_SIZE = {
    'K': 2**10,
    'M': 2**20,
    'G': 2**30,
    'T': 2**40
}

HUMANSIZE_PATTERN = re.compile('([1-9][0-9]*)([KMGT]|$)')


def humansize_int(humansize):
    match = HUMANSIZE_PATTERN.match(humansize)
    if match is None:
        raise ValueError("Invalid size string: %r" % humansize)
    size, suffix = match.groups()
    size = int(size)
    if suffix in SUFFIX_TO_SIZE:
        size *= SUFFIX_TO_SIZE[suffix]
    return size


def positive_int(value):
    num = int(value)
    if num <= 0:
        raise ValueError('%s is not a positive integer' % value)
    return num


def nonnegative_int(value):
    num = int(value)
    if num < 0:
        raise ValueError('%s is not a nonnegative integer' % value)
    return num
