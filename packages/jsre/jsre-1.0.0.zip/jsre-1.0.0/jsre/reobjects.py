'''
Regular Expression Module optimised for data recovery from raw byte data.

author: Howard Chivers

Copyright (c) 2015, Howard Chivers
All rights reserved.
'''

'''
Changes to 1.0.0b4
Added FIXED_ANCHOR start mode to prevent anchor scanning if re requires buffer start
Added NOINC_ANCHOR start mode to truncate scanning for re that effectively start {=any}*
Added scanning program for quick acquisition of anchor following newline
Corrected prefix generation (scan) to account for non-consuming groups
Refractored aux characters to place them in a separate tree root attribute
Asynchronous flag is depreciated (available as development flag XASYNCHRONOUS)
Added loop breaking in compulsory loops as well as *  (eg makes (re?){1000} efficient)
Corrected preference order of thread execution - smallest byte, smallest pc, largest count
Replaced vm thread management to allow binary list searches
Modified loop count allocation to avoid consuming counts for unbounded loops

****** Changes to 1.0.0b5
asynchronous depreciated for users
Bugfix - avoid control optimisation in subsequent repetitions of nested loops
Update vm for faster profiling (TRACE & TRACE_VERBOSE)
Updated test scripts to automate distribution
jsvm now includes __getstate__ and __setstate__
Improved compilation speed: updated reparser iterator, removed nondeterministic switch in charclass union
parser now interprets '{' as an unescaped character if not start of a repeat specification and '-' as a character where possible
repeated groups now capture unless marked by the user as non-capturing
no infinite loops - all loops limited to max (65535)
quantifers may now be modified as non-greedy, scope is next group or branch
vm memory image size now variable
various vm updates: policy-based implementation for lazy matches.
backreferences added
match() purge() added
truncated scanning for a re that starts *any* is removed due to restriction to counting loops
(note that dot-any kept - ie assumes that search restricted to counter limit after linestart)
vm auto-resizing for small res

****** Changes to 1.0.0b6
indexalt now applies to all alts (in the first set) not just character-only
change Match attribute from 'keyword' to 'keypattern'
tree optinisation now applies to all sub-expressions, not just word groups
'flags' now added to Match object as attribute
bugfix -  linestart/end templates (break between line end chars) and line scan (skip next line if single line end character)

****** changes to 1.0.0.b7
match added to __init__

****** changes to 1.0.0
loop counters zerod at ends of optional loops
guard now used for optional loops
unmeasured loops implemented for * and +
backrefMask provided to start (VM update)
'''

'''
Issues
'''

import logging
from collections import namedtuple

import jsvm

from jsre.dfacompiler import CharacterCompiler
from jsre.recompiler import compileProgram, writeStartToVM
from jsre.ucd import normaliseName, ENCODING_ALIAS
from jsre.reparser import parseRE
from jsre.reparser import INDEXALT, SECTOR, XTRACE, XTRACE_VERBOSE, XDUMPPARSE

jsreLog = logging.getLogger("jsre")
ReSpec = namedtuple('ReSpec', ('pattern', 'encoding', 'matchCount', 'nameMap', 'flags', 'endOrder'))

START_COMMAND_MASK     = 0xFFF0
START_ENDIAN_MASK      = 0x000F
COMPATIBLE_VM_VERSIONS = ["1.1.3", "1.1.3c"]
VM_TRACE               = 0x0001
VM_TRACE_VERBOSE       = 0x0002

_moduleCache = {}


class ReCompiler():
    '''
    Manages the compilation of multiple REs and encodings.

    The flags encodings and patterns specified for a single object of this class
    will be encoded into a single matching machine and searched simultaneously.
    This compiler builds a ``RegexObject`` object which wraps the matching machine
    used to run pattern matching.

    Several patterns may be compiled into the same execution object at the same
    time, and each may have different flags, encodings etc specified.

    For all methods:

    Parameters:
        pattern     a str regular expression.
        encoding    a list of encodings to search, default value is utf_8.
        flags       see compile()
        stride      the stride value for moving anchors.
        offset      a start offset into buffer to be searched.
        encodingSizeCorrection   divides match locations by specified value
                    to give string address.

        undocumented flags
            XTRACE          basic trace - just program counters
            XTRACE_VERBOSE  readable trace
            XDUMPPARSE      print parse tree
            XDUMPROG        print program

    Raises:
        SyntaxError     if the pattern is invalid.
    '''

    def __init__(self, pattern=None, encoding=('utf_8',), flags=0, offset=0, stride=0, encodingSizeCorrection=1):
        '''
        Allows a specification to be set (flags, encoding etc) and also a pattern.
        '''

        self.tvm   = jsvm.Jsvm()
        vm_version = jsvm.version()
        if vm_version not in COMPATIBLE_VM_VERSIONS:
            jsreLog.warning("Installed jsvm version {} is not in the compatibility list for this module, please upgrade".format(vm_version))

        self.charCompiler = CharacterCompiler(self.tvm)
        self.reMap        = {}
        self.stride       = 0
        self.offset       = 0
        self.encodingSizeCorrection = encodingSizeCorrection
        self.update(encoding=encoding, flags=flags, offset=offset, stride=stride)
        if pattern != None:
            self.setPattern(pattern)

    def update(self, encoding=None, flags=None, offset=0, stride=0):
        '''
        Update compiler encoding list, flags and options.

        Parameters specified using update will override any already set;
        they will apply to any subsequently specified patterns. See class for
        argument details.

        Parameters:
            encoding  a list of encodings to be used.
            flags     combination of required flags (I, M, S, etc), see ``compile()``.
            offset    start offset into buffer to be searched.
            stride    stride value for anchor moving.

            stride and offset are only required if the jsre.SECTOR flag is set,
        '''

        if encoding != None:
            if isinstance(encoding, str):
                # users may not use list or tuple for a single encoding
                self.encoding = (encoding,)
            else:
                self.encoding = encoding

        if flags    != None:
            self.flags    = flags
            if flags & SECTOR:
                if stride == None or offset == None:
                    msg = "Error call to update in ReCompiler - stride or offset not specified in sector mode"
                    jsreLog.error(msg)
                    raise ValueError(msg)
                self.offset   = offset
                self.stride   = stride
            else:
                self.offset   = 0
                self.stride   = 0

    def setPattern(self, pattern):
        '''
        Update the search specification to include the specified pattern.

        This pattern is compiled using any previously specified options or flags. The pattern
        specified will be searched in addition to any previously set patterns.

        Parameters:
            pattern: a regular expression, in str format.

        Raises:
            Sytnax Error    if pattern cannot be parsed.
        '''
        if self.flags & XTRACE:
            self.tvm.setTrace(VM_TRACE)
        if self.flags & XTRACE_VERBOSE:
            self.tvm.setTrace(VM_TRACE_VERBOSE)

        ptree = parseRE(pattern, self.flags)
        self.altMap = ptree.altMap
        if self.flags & XDUMPPARSE:
            ptree.print()

        # This short term cache is used to avoid building a new program when the
        # difference between encodings is only in the endian specification
        encCache = {}
        for enc_user in self.encoding:
            # get normalised encoding form
            enc_norm = normaliseName(enc_user)
            if enc_norm in ENCODING_ALIAS:
                enc_norm, endianMask = ENCODING_ALIAS[enc_norm]
            else:
                endianMask = 0

            # is the normalised form re-used
            if enc_norm in encCache:
                # difference should be only the endianMask, no need to parse or compile
                cachedStart = encCache[enc_norm]
                if endianMask == cachedStart[0]:
                    jsreLog.error("Duplicate encoding specified, will be ignored: {}".format(enc_user))
                    continue

                # build new start spec to point at existing prog, but with different endianMask
                startAttribs = (((cachedStart[1][0] & START_COMMAND_MASK) | (endianMask & START_ENDIAN_MASK)),) + cachedStart[1][1:]
                reIndex = writeStartToVM(self.tvm, startAttribs)
                reSpec = ReSpec(pattern, enc_user, cachedStart[2][2], cachedStart[2][3], cachedStart[2][4], cachedStart[2][5])
                self.reMap[reIndex] = reSpec

            else:
                # normal build
                ctree = self.charCompiler.compileCharacters(ptree, enc_norm, self.flags)
                self.charCompiler.writeCharactersToVM(ctree)
                ctree.endianMask = endianMask
                reIndex, matchCount, nameMap, startAttribs, endOrder = \
                    compileProgram(self.tvm, ctree, self.flags, self.offset, self.stride)
                reSpec = ReSpec(pattern, enc_user, matchCount, nameMap, self.flags, endOrder)
                self.reMap[reIndex] = reSpec
                encCache[enc_norm]  = (endianMask, startAttribs, reSpec)

    def compile(self):
        '''
        Builds a regular expression object which is used to execute the pattern matching.

        Returns
        RegexObject     a compiled regular expression pattern matcher
        '''

        if not hasattr(self, 'altMap'):
            raise Exception("Compile requested but no pattern set")
        return RegexObject(self.tvm, self.reMap, self.altMap, self.encodingSizeCorrection)


class RegexObject():
    ''' Provides the pattern matching interface together with the compiled matching engine.

    This pattern matcher is designed to simultaneously run several different combinations
    of regular expressions, flags, and encodings. As a consequence these attributes and
    others such as groups are provided in Match results, and not via this interface.

    The pattern matching process checks each pattern/encoding combination in turn; in
    consequence although order is preserved for individual patterns/encodings
    there is a possibility of overlaps between matches from different patterns. Search will
    also report from the first pattern/encoding to match.

    All methods have the same argument signature: (buffer [,start [,end [,endanchor]]] )

    The ability to specify both the buffer end and the end anchor allows long data streams
    to be split into blocks and ensure that all possible anchor points are searched without
    duplication and with a specified search window which is the overlap between blocks.

    Parameters:
        buffer  a byte object to search.

        start   the first byte in the buffer from which to search (default 0). It is assumed
                that the start will be on the minimum character word boundary of any encodings
                used (ie 2 byte for utf16, 4 byte for utf32).

        end     index of the last byte to be searched + 1 (i.e. normal Python slice end).
                A regular expression will fail if it gets to this point and has not matched.

        endAnchor The last byte to be used as an re anchor (ie the last position from
                  which the pattern match check should begin).

    '''

    def __init__(self, tvm, reMap, altMap, encodingSizeCorrection):
        ''' Build regular expression execution wrapper.

        Used internally by ReCompiler objects.

        Parameters:
            tvm      vm with compiled regular expressions
            reMap    dictionary: reStartCode -> ReSpec tuple
            altMap   dictionary: alt index -> original keypattern
            encodingSizeCorrection  used when search target is really a str which has been
                                  encoded into fixed number of bytes, this is the length in bytes.
        '''

        self._tvm    = tvm
        self._reMap  = reMap
        self._altMap = altMap
        self._encodingSizeCorrection = encodingSizeCorrection

    def search(self, *spec):
        '''
        Returns the first pattern match in the given buffer.

        Parameters:
            (buffer [,start [,end [,endanchor]]] ) - see RegexObject().

        Returns:
            Match    A Match object, or None.
        '''

        buf = spec[0]
        if not isinstance(buf, bytes):
            msg = "Buffer passed to search() does not have bytes type"
            jsreLog.error(msg)
            raise TypeError(msg)
        pos = 0 if len(spec) < 2 else spec[1]
        endpos = len(buf) if len(spec) < 3 else spec[2]
        endanchor = endpos if len(spec) < 4 else spec[3]
        if endanchor > endpos + 1:
            msg = "Last anchor position set beyond beyond buffer end"
            jsreLog.error(msg)
            raise ValueError(msg)
        res = self._tvm.findMatch(buf, pos, endanchor, endpos, True)
        if len(res) == 0:
            return None
        result = res[0]
        reSpec = self._reMap[result[0]]
        if reSpec.flags & INDEXALT:
            altWord = self._altMap[result[len(result) - 1][1]]
        else:
            altWord = None
        match = Match(result, (buf, pos, endanchor, endpos), reSpec, altWord, self._encodingSizeCorrection)
        return match

    def match(self, *spec):
        '''
        Returns a match if it an be made from a given start position in the given buffer.

        Parameters;
            (buffer [,start [,end ] )     see RegexObject().

            Note that the endanchor argument is not available in match().

        Returns:
            Match    A Match object, or None.
        '''
        buf = spec[0]
        pos = 0 if len(spec) < 2 else spec[1]
        endpos = len(buf) if len(spec) < 3 else spec[2]
        endanchor = pos
        return self.search(buf, pos, endpos, endanchor)

    def finditer(self, *spec):
        '''
        Returns an iterator over all matches in the given buffer.

        Parameters:
            (buffer [,start [,end [,endanchor]]] ) - see RegexObject().

        Returns:
            iterator    An iterator over Match objects.
        '''

        buf = spec[0]
        if not isinstance(buf, bytes):
            msg = "Buffer passed to finditer() does not have bytes type"
            jsreLog.error(msg)
            raise TypeError(msg)
        pos = 0 if len(spec) < 2 else spec[1]
        endpos = len(buf) if len(spec) < 3 else spec[2]
        endanchor = endpos if len(spec) < 4 else spec[3]
        if endanchor > endpos + 1:
            msg = "Last anchor position set beyond beyond buffer end"
            jsreLog.error(msg)
            raise ValueError(msg)

        res = self._tvm.findMatch(buf, pos, endanchor, endpos, False)
        return RegexIterator(res, (buf, pos, endpos, endanchor), self._reMap, self._altMap, self._encodingSizeCorrection)

    def findall(self, *spec):
        '''
        Returns all search matches as a list, or if multiple group matches within patterns,
        a list of tuples.

        The results are returned as strings (str), the successful encoding is
        used to decode the byte array and provide a string version of the result.

        Parameters:
            (buffer [,start [,end [,endanchor]]] ) - see RegexObject().

        Returns:
        A list of strings or list of tuples containing strings, see Match.groups().
        '''

        hits = self.finditer(*spec)
        res = []
        for match in hits:
            res.append(match.groups())
        return res


class RegexIterator():
    ''' The match iterator that is returned from finditer.
    '''

    def __init__(self, res, searchSpec, reMap, altMap, encodingSizeCorrection):
        self._res    = res
        self._search = searchSpec
        self._reMap  = reMap
        self._altMap = altMap
        self._encodingSizeCorrection = encodingSizeCorrection

    def __iter__(self):
        self._next = 0
        return self

    def __next__(self):
        if self._next >= len(self._res):
            raise StopIteration
        result = self._res[self._next]
        self._next += 1
        reSpec = self._reMap[result[0]]
        if reSpec.flags & INDEXALT:
            altWord = self._altMap[result[len(result) - 1][1]]
        else:
            altWord = None
        return Match(result, self._search, reSpec, altWord, self._encodingSizeCorrection)


class Match():
    '''
    Describes a single successful match.

    A Match object always evaluates as true.

    As far as possible this class provides the same interface as the standard Python re Match \
    together with some extensions which allow the retrieval of the expression and \
    encoding associated with a particular match, and (if INDEXALT) the keypattern component \
    of the pattern which matched.

    The characters matched by the regular expression are always returned as a string by decoding \
    the byte search target using whatever encoding was successful.

    Usually the (start, stop) indexes of a match group are returned as byte indexes. However if \
    *encodingSizeCorrection* was set (>1) as a ``ReCompiler`` option the indexes are divided by \
    the given value to be corrected to string indexes.

    Methods that require a group index as an argument can instead be provided with a group name, if the
    group is named in the regular expression.

    Available class properties:
        pos        the start position specified for this match (see RegexObject).
        endpos     the end of buffer specified for this match.
        endAnchor  the last anchor position allowed for this match.
        lastindex  the integer index of the last matched capturing group.
        lastgroup  the name of the last matched capturing group.
        re         the regular expression used for this match.
        encoding   the encoding used for this match.
        flags      the flags used to compile this re.
        buf        the bytes buffer used for this match.
        keypattern    the keypattern successful in this match (if present and  if INDEXALT set)
    '''

    def __init__(self, res, searchSpec, reSpec, altWord, encodingSizeCorrection):
        '''
        Paramaters:
           res            A vm result [re, (match-0-first, match-0-last+1)...]
           searchSpec    (buffer, start, end, stop)
           reSpec         An ReSpec named tuple
         '''

        self._res       = res
        self._search    = searchSpec
        self._reSpec    = reSpec
        self._gpCache   = {}
        self._encodingSizeCorrection = encodingSizeCorrection

        self._matchCount = 1
        for i in range(reSpec.matchCount, 1, -1):
            if res[i][0] != -1:
                self._matchCount = i
                break

        self.pos        = searchSpec[1]
        self.endpos     = searchSpec[2]
        self.endAnchor  = searchSpec[3]
        self.re         = reSpec.pattern
        self.buf        = searchSpec[0]
        self.encoding   = reSpec.encoding
        self.flags      = reSpec.flags
        self.keypattern    = altWord
        self.lastgroup  = None
        self.lastindex  = None

        # find which reported group was last to be matched
        if len(res) > 2:
            for i in range(2, len(res)):
                if res[i][0] != -1:
                    if self.lastindex == None or reSpec.endOrder[i - 1] > reSpec.endOrder[self.lastindex]:
                        self.lastindex = i - 1

        # if a group was found, look up name if present
        if self.lastindex != None:
            for name in reSpec.nameMap:
                if reSpec.nameMap[name] == self.lastindex:
                    self.lastgroup = name
                    break

    def __bool__(self):
        return True

    def group(self, *args):
        '''
        Returns a decoded substring for one or more match subgroups.

        Parameters:
            group     One or more group indexes or names.
                      Group 0 is always the whole match and group names may be used
                      instead of indexes.

        Returns:
            If there is a single argument a string, otherwise a tuple of strings.
        '''

        if len(args) == 0:
            return self._fetchMatchString(0)
        elif len(args) == 1:
            return self._fetchMatchString(self._checkGroupIndex(args[0]))
        res = []
        for gid in args:
            res.append(self._fetchMatchString(self._checkGroupIndex(gid)))
        return tuple(res)

    def groups(self, *args):
        '''
        Returns a tuple of the subgroups of the match.

        Parameters:
            default  specifies the value for groups that did not participate in the match.
                     if not specified None is the default.

        Returns:
            A tuple of decoded strings, with groups that failed to match replaced by
            the default value.
        '''

        default = None if len(args) == 0 else args[0]
        res = []
        for gid in range(self._matchCount):
            val = self._fetchMatchString(gid)
            if val == None:
                val = default
            res.append(val)
        return tuple(res)

    def groupdict(self, *args):
        '''
        Returns a dictionary of named group matches.

        Parameters:
            default specifies the value for groups that did not participate in the match,
                    if not provided None is the default (no keypattern needed).

        Returns:
            A dictionary which maps group name to group string matched.
        '''

        default = None if len(args) == 0 else args[0]
        res = {}
        for ri in self._reSpec.nameMap:
            gid = self._reSpec.nameMap[ri]
            val = self._fetchMatchString(gid)
            if val == None:
                val = default
            res[ri] = val
        return res

    def start(self, *args):
        '''
        Return index of start of group, or of the whole match.

        Start and end together allow retrieval of the bytes in the usual way:
        match.buf[start(i):end(i)]

        Parameters:
            group   The ID or name of the group. If not specified, group 0
                    (the whole match) is returned. (no keypattern needed.)

        Returns:
            An integer index to bytes in the search target, or to utf32 string
            position (see Match() documentation.
        '''

        return self._getGroupPosition(0, *args)

    def end(self, *args):
        '''
        Returns:
            The end of group, or of whole match, see ``start()``.
        '''

        return self._getGroupPosition(1, *args)

    def span(self, *args):
        '''
        Returns:
            The start and end of match as a tuple. See ``start()``.
        '''

        start = self.start(*args)
        end   = self.end(*args)
        return start, end

    #
    # additional public methods not in re
    #

    # helper methods

    def _fetchMatchString(self, gid):
        ''' Fetch the match string for the given group.

            This decodes from the raw buffer into a string using
            the encoding of the re. Result is cached.
        '''

        if gid >= self._matchCount:
            return None
        if gid not in self._gpCache:
            rid = gid + 1
            if self._res[rid][0] == -1:
                return None
            self._gpCache[gid] = self.buf[self._res[rid][0]:self._res[rid][1]]\
                                    .decode(encoding=self._reSpec.encoding, errors='ignore')
        return self._gpCache[gid]

    def _getGroupPosition(self, end, *args):
        ''' Returns start or end of group position
            correct if required from bytes to utf32 string position
        '''

        gid = 0 if len(args) == 0 else args[0]
        pos = self._res[self._checkGroupIndex(gid) + 1][end]
        if self._encodingSizeCorrection > 1:
            pos = pos // self._encodingSizeCorrection
        return pos

    def _checkGroupIndex(self, gid):
        ''' Check if a group id is valid, and convert name to ID if required.
        '''

        if isinstance(gid, str):
            if gid not in self._reSpec.nameMap:
                raise KeyError("Request for invalid Group name: {}".format(gid))
            index = self._reSpec.nameMap[gid]
        else:
            index = gid
        if index > len(self._res) - 2:
            raise IndexError("Request for invalid Group ID: {:d}".format(index))
        return index

# *********************************************************************
#  Module level functions similar to python re
#
#  The ability to take string targets for searching is really for testing
#  and demonstration rather than the normal use for this engine which is
#  designed to search bytes
# *********************************************************************


def search(pattern, target, **kargs):
    '''
    Find the first match location of a pattern in the target.

    Encodings are searched in turn and search will halt at the first to match.
    If encodings are specified then 'first' may not be the lowest index that
    could be matched by any of the possible encodings.

    Regular expressions and associated encodings are cached - if the same
    combination is repeated the execution engine is not rebuilt.

    Parameters:
        pattern   the regular expression, as a str
        target    the search target, as a byte buffer or str (see above)

    Keywords:
        encoding  list of required encodings (default utf-8 unless target is a str, in which case the default is utf-32-be)
        flags     control flags (see ``compile()``).
        stride    stride/offset used with SECTOR flag, see ``compile()``.
        offset

    Returns:
        A Match object, or None.
    '''

    regex, buf = _findspec(pattern, target, **kargs)
    return regex.search(buf)


def match(pattern, target, **kargs):
    '''
    Test if a match can be made from the start of the target string.

    Encodings are searched in turn and search will halt at the first
    to match.

    Regular expressions and associated encodings are cached - if the same
    combination is repeated the execution engine is not rebuilt.

    Parameters, keywords, returns, as match()
    '''

    regex, buf = _findspec(pattern, target, **kargs)
    return regex.match(buf)


def finditer(pattern, target, **kargs):
    '''
    Returns a match iterator for the regular expression pattern over the search target.

    Parameters:
        pattern   the regular expression, as a str
        target    the search target, as a byte buffer or str (see above)

    Keywords:
        encoding  list of required encodings (default utf-8 unless target is a str, in which case the default is utf-32-be)
        flags     control flags (see ``compile()``).
        stride    stride/offset used with SECTOR flag, see ``compile()``.
        offset

    Returns:
        An iterator over Match objects.
    '''

    regex, buf = _findspec(pattern, target, **kargs)
    return regex.finditer(buf)


def findall(pattern, target, **kargs):
    '''
    Returns all search hits as a list of strings, or a list of tuples.

    If a regular expression has sub-match groups then the result will be a tuple for each
    overall match. Non-matching groups will return a ``None`` entry in the tuple.

    Parameters:
        pattern   the regular expression, as a str
        target    the search target, as a byte buffer or str (see above)

    Keywords:
        encoding  list of required encodings (default utf-8 unless target is a str, in which case the default is utf-32-be)
        flags     control flags (see ``compile()``).
        stride    stride/offset used with SECTOR flag, see ``compile()``.
        offset

    Returns:
        A list of strings or list of tuples containing strings.
    '''

    hits = finditer(pattern, target, **kargs)
    res = []
    for match in hits:
        res.append(match.groups())
    return res


def compile(pattern, **kargs):
    '''
    Compile a regular expression into a regular expression object.

    Is equivalent to RECompile( ... ).compile()

    Parameters:
        pattern:    a regular expression, in str format (bytes are not an option).

    Keywords:
        encoding    a list of encodings to search (default = utf_8).
        flags:
            jsre.I or jsre.IGNORECASE
            Character matching is case insensitive. Basic unicode folding is implemented.
            (ie equivalent characters are not just upper and lower case.)

            jsre.M or jsre.MULTILINE
            ^ and $ match the start/end of each line well as the buffer start/end.

            jsre.S or jsre.DOTALL
            dot '.' matches line ends as well as all other characters.

            jsre.X or jsre.VERBOSE
            Ignore while space including line breaks and comments within the regular expression
            outside character classes. A comment may be placed between '#' and a line end.

            jsre.INDEXALT
            Index top level alternatives - e.g. index keypattern hit in list of alternative words this
            is more scalable than using groups to identify matched alternatives. Only keywords
            are indexed, not other alternative expressions.

            jsre.SECTOR
            Specify stride and offset of match anchors. e.g. stride = 512, offset = 0 will test
            at the start of every sector of a disk image. Otherwise stride and offset are not
            needed.

        stride    the stride value for moving anchors.
        offset    a start offset into buffer to be searched.
        encodingSizeCorrection:   divide factor to give string address for fixed byte
                                Unicode encoding. This is set automatically by the module
                                functions if a string input is provided. It can be used
                                manually with the object methods to achieve the same result.
    '''

    if not isinstance(pattern, str):
        raise ValueError("Error: pattern provided to re compiler must be a string")
    if 'flags' not in kargs:
        kargs['flags'] = 0
    kargs['pattern'] = pattern
    key = ','.join('{}:{}'.format(key, val) for key, val in sorted(kargs.items()))
    if key not in _moduleCache:
        _moduleCache[key] = ReCompiler(**kargs).compile()
    return _moduleCache[key]


def purge():
    '''
    Clear regular expression module cache.
    '''
    global _moduleCache
    _moduleCache = {}


def _getModuleCache():
    '''
    Returns module cache, for testing
    '''
    return _moduleCache


def _findspec(pattern, target, **kargs):
    '''
    Preprocessing module level search target.

    If the buffer is a string and encoding is not specified then utf32 is used
    to allow byte indexing to be reliably converted to string position.
    '''

    if isinstance(target, str):
        if 'encoding' not in kargs:
            kargs['encoding']             = 'utf_32_be'
            kargs['encodingSizeCorrection'] = 4
        if isinstance(kargs['encoding'], str):
            buf = target.encode(encoding=kargs['encoding'])
        else:
            buf = target.encode(encoding=kargs['encoding'][0])
    else:
        buf = target
    regex = compile(pattern, **kargs)
    return regex, buf
