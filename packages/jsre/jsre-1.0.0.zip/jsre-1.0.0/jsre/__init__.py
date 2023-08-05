'''
jsre provides a regular expression machine for efficiently searching large byte buffers.

@author: Howard Chivers

Copyright (c) 2015, Howard Chivers
All rights reserved.
'''

from jsre.reobjects import compile, search, match, findall, finditer, purge
from jsre.reobjects import ReCompiler

from jsre.reparser import I, IGNORECASE, M, MULTILINE, S, DOTALL, X, VERBOSE, INDEXALT, SECTOR
from jsre.reparser import XDUMPPARSE
# from jsre.reparser import XASYNCHRONOUS, XTRACE, XTRACE_VERBOSE, XDUMPPROG
