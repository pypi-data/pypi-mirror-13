''' Module contains functions required for hashing file data

    Guaranteed algorithms are:
    * md5
    * sha1
    * sha224
    * sha256
    * sha384
    * sha512
 '''
from __future__ import print_function
import os
import hashlib

def make_hash(filename, algo='md5'):
    '''
        Returns an md5 hash of the data in the file.
        For use as an imported imported function

        algo keyword argument should be one of the following:

        * md5
        * sha1
        * sha224
        * sha256
        * sha384
        * sha512

    '''
    m = getattr(hashlib, algo)()
    try:
        path = os.path.abspath(filename)
        with open(path, 'rb') as fname:
            contents = fname.read()
            m.update(contents)
        return m.hexdigest()
    except IOError as err:
        print('[Errno {0}]: {1}'.format(err.errno, err.strerror))
        raise err
