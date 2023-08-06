from __future__ import print_function
from . import checkmd5 as c
import sys
import os
import hashlib
make_hash = c.make_hash
_FLAGS = ('-a', '--algo')
__version__ = '0.2.0'

def usage():
    print('Usage: md5checker "path-to-file" [options]')

def list_algorithms():
    ''' List available algorithms '''
    algorithms = sorted(list(hashlib.algorithms_guaranteed))
    prompt = 'Available hash types'
    print(prompt)
    print('-' * len(prompt) + '\n')
    print('\n'.join(algorithms))

def main():
    ''' Entry point for the application script '''
    args = sys.argv
    length = len(args)

    if length < 2 or length > 4:
        usage()
    elif length == 2:
        if args[1] == '-v' or args[1] == '--version':
            print(__version__)
        elif args[1] == '-a' or args[1] == '--algo':
            list_algorithms()
        else:
            print(make_hash(args[1]))
    elif length == 4:
        flag = args[2]
        if flag in _FLAGS:
            print(make_hash(args[1], algo=args[3]))
        else:
            print('Optional flags are -a or --algo')
            
