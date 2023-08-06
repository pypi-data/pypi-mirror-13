from __future__ import print_function
from . import checkmd5 as c
import sys
import os
make_hash = c.make_hash

def main():
    ''' Entry point for the application script '''
    args = sys.argv
    if len(args) != 2:
        print('Usage: md5checker "path-to-file"')
    else:
        print(make_hash(sys.argv[1]))
