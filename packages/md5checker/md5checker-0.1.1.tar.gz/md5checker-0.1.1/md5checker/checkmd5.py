''' Module contains functions required for hashing file data '''
from __future__ import print_function
import sys
import os
import hashlib

def make_hash(filename):
    '''
        Returns an md5 hash of the data in the file.
        For use as an imported imported function
    '''
    m = hashlib.md5()
    try:
        path = os.path.abspath(filename)
        with open(path, 'rb') as fname:
            contents = fname.read()
            m.update(contents)
        return m.hexdigest()
    except IOError as err:
        print('[Errno {}]: {}'.format(err.errno, err.strerror))
        raise err
