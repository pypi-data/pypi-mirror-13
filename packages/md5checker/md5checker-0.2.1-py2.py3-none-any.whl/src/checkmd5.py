#!/usr/bin/env python
''' Check md5 has of file '''
from __future__ import print_function
import sys
import os
import hashlib

def make_file_hash(filename):
    ''' Creates a hash for the file given '''
    md5 = hashlib.md5()
    try:
        path = os.path.abspath(filename)
        with open(path, 'rb') as fname:
            contents = fname.read()
            md5.update(contents)
        return md5.hexdigest()
    except IOError as err:
        print('[Errno {}]: {}'.format(err.errno, err.strerror))
        raise err

if __name__ == '__main__':
    if len(sys.argv) > 1:
        FILE_NAME = sys.argv[1]
        print(make_file_hash(FILE_NAME))
    else:
        print('Usage: python checkmd5.py path-to-file')
        sys.exit(1)
