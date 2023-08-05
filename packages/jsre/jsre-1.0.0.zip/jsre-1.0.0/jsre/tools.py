#!python
'''
Runs tests and compilation for jsre.

@author: Howard Chivers

Copyright (c) 2015, Howard Chivers
All rights reserved.

'''
from codecs import lookup

from sys import argv
from jsre.ucd import compileEncoding, normaliseName, isEncodingInstalled, DEFAULT_ENCODINGS

usage = '''
usage:
tools test                    runs jsre unit tests
tools compile [encoding]      installs default encodings, or the specified encoding

Encodings must be installed before use, the default encodings include the normal unicode
encodings (utf_8, utf_16_be, utf_16_le, utf_32_be, utf_32_le), ascii and a range of code pages.
'''


def abort(msg):
    print('Error: ' + msg)
    print(usage)
    exit(1)

if __name__ == '__main__':
    if len(argv) < 2:
        abort('Invalid command line, no command given.')
    if argv[1] == 'test':
        print("Running jsre tests")
        import test
        test.runTest()
        exit(0)
    elif argv[1] == 'compile':
        if len(argv) == 2:
            print("Compiling default encodings")
            for encoding in DEFAULT_ENCODINGS:
                compileEncoding(encoding)
        else:
            encoding = normaliseName(argv[2])
            if isEncodingInstalled(encoding):
                abort("Encoding {} is already installed".format(encoding))
            try:
                lookup(encoding)
            except:
                abort("Encoding {} is not known - not a valid Python codec".format(encoding))
            if encoding in ('utf_32', 'utf_32_le', 'utf_16', 'utf_16_le'):
                abort("Error - encoding {} not valid, must specify -be".format(encoding))
            print('Compiling Unicode properties for encoding: {}'.format(encoding))
            compileEncoding(encoding)
        print("Compile Complete")
    else:
        abort('Command not recognised: {}'.format(argv[1]))
