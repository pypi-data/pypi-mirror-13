'''
Regular expression parser for the jsvm virtual machine.

@author: Howard Chivers

Copyright (c) 2015, Howard Chivers
All rights reserved.

'''

import re
import logging
import copy
from collections import namedtuple
from jsre.ucd import getPropertyValueNames

parseLog = logging.getLogger("parser")

VM_COUNT_UNMEASURED = 0xFFFF   # loop length that signifies unmeasured.
VM_MAX_STATE_SIZE   = 16384    # maximum number of character states allowed in vm
MAX_TREE_DEPTH      = 255      # stack limit on tree iterator

# jsre flags. all here to keep together
''' be compatible with re's use of flags:
ASCII      = 0x100
IGNORECASE = 0x2
LOCALE     = 0x4
MULTILINE  = 0x8
DOTALL     = 0x10
VERBOSE    = 0x40
'''
I              = 0x2
IGNORECASE     = 0x2      # any individual characters are case insensitive
M              = 0x8
MULTILINE      = 0x8      # ^ and $ match line boundaries as well as start and end of buffer
S              = 0x10
DOTALL         = 0x10     # '.' matches line endings as well as all other characters
X              = 0x40
VERBOSE        = 0x40     # allow while space and comments in re
INDEXALT       = 0x200    # index highest level of alternatives
SECTOR         = 0x400    # use stride and offset to specify possible anchor positions

# Undocumented flags
XTRACE         = 0x1000    # run VM with trace enabled
XTRACE_VERBOSE = 0x2000    # set verbose (readable) trace
XDUMPPROG      = 0x4000    # print compiled program
XDUMPPARSE     = 0x8000    # print parse tree
XASYNCHRONOUS  = 0x10000   # move anchor a byte at a time, not default character byte size

# node types in parse tree
TYPE_GROUP     = 0x1
TYPE_CLASS     = 0x2
TYPE_CHAR      = 0x4
TYPE_HEX       = 0x8
TYPE_PROPERTY  = 0x10
TYPE_DOT       = 0x20
TYPE_PROG      = 0x40
TYPE_ALT       = 0x80
TYPE_REPEAT    = 0x100
TYPE_RELATION  = 0x200
TYPE_RANGE     = 0x400
TYPE_CLASSREF  = 0x800   # reference to an identical class
TYPE_CHARCLASS = 0x1000  # has character class tree attached
TYPE_COMPILED  = 0x2000  # has state index
TYPE_AUXCHARS  = 0x4000  # childList contains additional characters or compiled refs


# TYPE_HAS_CHILD is used for initialisation, note that PROG may also add children
TYPE_HAS_CHILD          = TYPE_GROUP | TYPE_CLASS | TYPE_RELATION | TYPE_REPEAT | TYPE_ALT
TYPE_IS_CHARACTER       = TYPE_CLASS | TYPE_CHAR | TYPE_HEX | TYPE_DOT | TYPE_PROPERTY | TYPE_COMPILED
TYPE_VALID_IN_RELATION  = TYPE_CLASS | TYPE_CHAR | TYPE_HEX | TYPE_DOT | TYPE_PROPERTY | TYPE_RELATION
TYPE_VALID_REPEAT_CHILD = TYPE_CLASS | TYPE_CHAR | TYPE_HEX | TYPE_DOT | TYPE_PROPERTY | TYPE_GROUP

TYPE_LOOKUP     = {0x1: 'group    ',
                   0x2: 'class    ',
                   0x4: 'character',
                   0x8: 'hex value',
                   0x10: 'property ',
                   0x20: 'dot',
                   0x40: 'action   ',
                   0x80: 'alternate',
                   0x100: 'repeat   ',
                   0x200: 'relation ',
                   0x400: 'tmp-range',
                   0x800: 'class-ref',
                   0x1000: 'compiled ',
                   0x2000: 'loaded cc'}

# node binary attributes (node.attr)
AT_NOTGREEDY     = 0x1
AT_NOTCONSUME    = 0x2
AT_NOTCAPTURE    = 0x4
AT_PROG_CHARS    = 0x8
AT_NOT           = 0x10
AT_COMBINE_AND   = 0x20
AT_COMBINE_DIFF  = 0x40
AT_DISJOINT      = 0x100
AT_B_NODE        = 0x200
AT_CONTROLLING   = 0x400
AT_ANY           = 0x800
AT_DOT           = 0x1000

ATTRIBUTE_LOOKUP = {AT_NOTGREEDY: 'not-greedy',
                    AT_NOTCONSUME: 'not-consume',
                    AT_NOTCAPTURE: 'not-capture',
                    AT_PROG_CHARS: 'prog_characters',
                    AT_NOT: ' NOT ',
                    AT_COMBINE_AND: 'and-relation',
                    AT_COMBINE_DIFF: 'diff-relation',
                    AT_DISJOINT: 'disjoint',
                    AT_CONTROLLING: 'controlling',
                    AT_ANY: 'any',
                    AT_DOT: 'dot'}

#program types (node.action)
PROG_TEXT_START    = 0x1   # ^
PROG_TEXT_END      = 0x2   # $
PROG_BUFF_START    = 0x4   # \A
PROG_BUFF_END      = 0x8   # \z
PROG_WBOUNDARY     = 0x10  # \b
PROG_NWBOUNDARY    = 0x20  # \B
PROG_GRAPHEME      = 0x40  # \X
PROG_BACKREFERENCE = 0x80  # \nn ot (?P...)

PR_DOT              = 'dot_all'          # this is without crlf

# lookup also includes aux characters
ACTION_LOOKUP      = {PROG_TEXT_START: 'start of text    ',
                      PROG_TEXT_END: 'end of text      ',
                      PROG_BUFF_START: 'buffer start only  ',
                      PROG_BUFF_END: 'buffer end only    ',
                      PROG_WBOUNDARY: 'word boundary    ',
                      PROG_NWBOUNDARY: 'not word boundary',
                      PROG_GRAPHEME: 'grapheme break',
                      PROG_BACKREFERENCE: 'backreference',
                      'CHAR_DOT': 'dot character'
                     }

GROUP_SIGNATURES    = (('??', AT_NOTGREEDY), ('?=', AT_NOTCONSUME), ('?:', AT_NOTCAPTURE))

ESCAPE_CHARACTER    = {'a': '\a',
                       'f': '\f',
                       'n': '\n',
                       'r': '\r',
                       't': '\t',
                       'v': '\v',
                       '\\': '\\',
                       "'": "'",
                       '"': '"',
                       '(': '(',
                       ')': ')',
                       '[': '[',
                       ']': ']',
                       '{': '{',
                       '}': '}',
                       '|': '|',
                       '^': '^',
                       '$': '$',
                       '+': '+',
                       '*': '*',
                       '?': '?',
                       '.': '.'
                       }

CLASS_ESCAPE_CHARACTER = {'a': '\a',
                          'b': '\b',
                          'f': '\f',
                          'n': '\n',
                          'r': '\r',
                          't': '\t',
                          'v': '\v',
                          '\\': '\\',
                          "'": "'",
                          '"': '"',
                          '[': '[',
                          ']': ']',
                          '&': '&',
                          '|': '|',
                          '-': '-'
                          }

                        # open, (close, exclude between)
BRACKETS             = {'(': (')', '['),
                        '[': (']', ''),
                        '{': ('}', '')}

# NOTE parser will convert ^ to \A and $ to \z unless the MULTILINE flag is set
# compiler can assume that ^ $ are multiline programs

PROG_TYPE           = {'^': PROG_TEXT_START,
                       '$': PROG_TEXT_END,
                       'A': PROG_BUFF_START,
                       'z': PROG_BUFF_END,
                       'b': PROG_WBOUNDARY,
                       'B': PROG_NWBOUNDARY,
                       'X': PROG_GRAPHEME}

PROG_BACKSLASH       = 'AzbBX'

CLASS_CHARACTER     = {                # property of character
                       'd': 'digit',
                       'D': 'not_digit',
                       's': 'blank',
                       'S': 'not_blank',
                       'w': 'word',
                       'W': 'not_word'
                       }

CLASS_COMBINER      = {'|': None,
                       '&': AT_COMBINE_AND,
                       '-': AT_COMBINE_DIFF
                      }

# repeat specs = (re, first (-ve is suBmatch address), last (ditto), submatch for '?')
REPEAT_SPECS        = ((r'\*(\??)', 0, VM_COUNT_UNMEASURED, 1),
                      (r'\?(\??)', 0, 1, 1),
                      (r'\+(\??)', 1, VM_COUNT_UNMEASURED, 1),
                      (r'\{ *(\d{1,10}) *\}(\??)', -1, -1, 2),
                      (r'\{ *, *(\d{1,10}) *\}(\??)', 0, -1, 2),
                      (r'\{ *(\d{1,10}) *, *\}(\??)', -1, VM_COUNT_UNMEASURED, 2),
                      (r'\{ *(\d{1,10}) *, *(\d{1,10}) *\}(\??)', -1, -2, 3))

#other res for parsing
RE_NAMED_GROUP        = r'\?P< *(\w{1,20}) *>'
RE_CODE_POINT         = r'u([0-9a-fA-F]{4})|U([0-9a-fA-F]{8})'
RE_HEX_BYTE           = r'x([0-9a-fA-F]{2})'
RE_UNICODE_PROPERTY   = r'[pP]([LMNSPZC])|[pP]\{([ \-_\w]{1,50})\}|[pP]\{([ \-_\w]{1,50})[:=]([ \-_\w]{1,50})\}'
RE_VERBOSE_COMMENT    = r'#.*'
RE_B_BACKREFERENCE    = r'3[1-2]|[1-2][1-9]|[1-9]'
RE_N_BACKREFERENCE    = r'\?P= *(\w{1,20}) *\)'


def parseRE(pattern, flags):
    '''Parse a regular expression and return the parse tree

    Params:
        pattern    string which is the regular expression
                   it does not need to be enclosed in a group unless the whole
                   expression requires a qualified group (e.g. non-greedy)
                   the whole string will be regarded as a regular expression
                   no start and end delimeters are expected

        dotall    specifies if the '.' should be treated as excluding line
                  breaks (False, default) or include all characters (True)

    Returns:
        ReComponent which is the root of the parse tree

    Raises:
        SyntaxError for a faulty pattern
    '''

    reparser = ReParser(pattern, flags)
    root = ReComponent(0, TYPE_GROUP)
    reparser.parseGroup(0, len(pattern), root)

    # remember the parsed pattern in the tree root
    root.pattern = pattern

    # index alt children
    altIndex = 0
    root.altMap = {-1: None}  # altIndex -> word pattern
    for comp in root.filteredBy(TYPE_ALT):
        for child in comp.childList:
            child.altIndex = altIndex
            root.altMap[altIndex] = child.pattern
            altIndex += 1
        break  # only mark first alternate set
    return root


class ReParser():
    '''
    Build a parse tree given an re pattern.

    This class is primarily a tokeniser using recursive descent over [] and ()
    It is not essential to keep a reference to a class object between different
    patterns - the purpose of the class is to support a namespace during
    recursive descent.

    Public Methods:
        parseGroup    parse a pattern and add the tree to a root ReComponent
    '''

    def __init__(self, pattern, flags):
        '''Initialise the tokeniser.

        Params:
        dotall      if true '.' matches all characters,
                    otherwise does not match line endings
        '''
        self.pattern     = pattern
        if not pattern or pattern == '':
            syntaxError('', 0,
                        'Syntax error - empty regular expression pattern')
        self.groupNames = []

        self.verbose = True if flags & VERBOSE else False
        self.parseAction = {'(': self._gpTokenBracket,
                            '^': self._gpTokenProg,
                            '$': self._gpTokenProg,
                            '.': self._gpTokenDot,
                            '\\': self._gpTokenBackslash,
                            '[': self._gpTokenCharacterClass,
                            '*': self._gpTokenRepeat,
                            '?': self._gpTokenRepeat,
                            '+': self._gpTokenRepeat,
                            '{': self._gpTokenRepeat,
                            '|': self._gpTokenRelation,
                            '#': self._gpTokenHash,
                            ' ': self._gpTokenWhiteSpace,
                            '\f': self._gpTokenWhiteSpace,
                            '\n': self._gpTokenWhiteSpace,
                            '\r': self._gpTokenWhiteSpace,
                            '\t': self._gpTokenWhiteSpace,
                            '\v': self._gpTokenWhiteSpace,
                            '\u0085': self._gpTokenWhiteSpace,
                            '\u2028': self._gpTokenWhiteSpace,
                            '\u2029': self._gpTokenWhiteSpace,
                            }

        self.classAction = {'[': self._gpTokenCharacterClass,
                            '|': self._clTokenRelation,
                            '&': self._clTokenRelation,
                            '-': self._clTokenRelation,
                            '\\': self._clTokenBackslash
                            }

    #*************************************************************
    #    tokenise group
    #*************************************************************

    def parseGroup(self, start, end, parent):
        '''parse a group '(...)' or root, entry point for parser.

        The given pattern is the content of the group, the parser returns
        a tree rooted at parent. The parent type must be group, but it
        may be modified in parsing if there is a top-level alternate structure
        within the group (...|...).

        Args:
            start      first byte in pattern to parse
            end        last byte+1 in pattern to parse
            parent     an ReComponent object of type group to which the tree
                       will be attached.

        Returns:
            parent     input parent modified to attach parse tree as children

        Raises:
            SyntaxError for a faulty pattern
        '''

        #tokenize the string into components
        posn = start
        while posn < end:
            posn = self.parseAction.get(self.pattern[posn],
                                        self._gpTokenOther)(posn, end, parent)

        # bind repeat loop to previous entry
        toDo = self._listIndexOfType(parent.childList, TYPE_REPEAT)
        if len(toDo) > 0:
            newChildList = []
            if toDo[0] == 0:
                syntaxError(self.pattern,
                            start,
                            'Syntax error - RE or group starts with a repeat specification (nothing to repeat)')
            toDo.append(999999)
            j = 0
            for i, newChild in enumerate(parent.childList):
                if i == toDo[j] - 1:
                    #at entry before loop
                    if not (newChild.type & TYPE_VALID_REPEAT_CHILD):
                        syntaxError(self.pattern,
                                    newChild.start,
                                    'Syntax error - invalid token before repeat')
                    parent.childList[i + 1].childList = [newChild]
                    parent.childList[i + 1].start     = newChild.start
                    j += 1
                else:
                    newChildList.append(parent.childList[i])
            parent.childList = newChildList

        #if there are any alternate tokens, make sub-groups
        # build work list of alt spans
        toDo = []
        left = 0
        for i, child in enumerate(parent.childList):
            if child.type == TYPE_ALT:
                toDo.append((left, i))
                left = i + 1

        # process L-R
        if len(toDo) > 0:
            newChildList = []
            toDo.append((left, len(parent.childList)))
            for i in range(len(toDo)):
                if toDo[i][0] == toDo[i][1]:
                    syntaxError(self.pattern,
                                start,
                                'Syntax error - empty alternative')

            # fold children under alt
            for i in range(len(toDo)):
                newComp = parent.childList[toDo[i][0]]
                # add new group if necessary to contain alt child
                if (toDo[i][1] - toDo[i][0] > 1) or (newComp.type != TYPE_GROUP):
                    newComp = ReComponent(parent.childList[toDo[i][0]].start, TYPE_GROUP)
                    newComp.attr |= AT_NOTCAPTURE
                    for j in range(*toDo[i]):
                        newComp.childList.append(parent.childList[j])
                    self._checkIfGroupLazy(newComp)
                newend = parent.childList[toDo[i + 1][0]].start - 1 if i < len(toDo) - 1 else end
                newComp.pattern = self.pattern[newComp.start:newend]
                newChildList.append(newComp)

            # need new ALT component between parent and new children
            newComp = ReComponent(start, TYPE_ALT)
            newComp.childList = newChildList
            parent.childList  = [newComp]

        # update group to lazy if quantifiers set
        self._checkIfGroupLazy(parent)

    def _gpTokenBracket(self, start, end, parent):
        # find the matching end bracket
        endpos = self._findBracketEnd(start + 1, end, '(')
        gpstart = start + 1

        # ignore comment groups
        if self.pattern.startswith('(?#', start):
            return endpos + 1

        # backreference extensions
        match = re.compile(RE_N_BACKREFERENCE).match(self.pattern, gpstart, end)
        if match:
            newComp = ReComponent(start, TYPE_PROG)
            newComp.action = PROG_BACKREFERENCE
            newComp.name   = match.group(1)
            if newComp.name not in self.groupNames:
                syntaxError(self.pattern,
                            start,
                            'Backreference name ({}) is not a group name'.format(newComp.name))
            parent.childList.append(newComp)
            return match.end(0)

        newComp = ReComponent(start, TYPE_GROUP)
        gpend   = endpos
        # check group attributes
        for a in GROUP_SIGNATURES:
            if self.pattern.startswith(a[0], gpstart):
                newComp.attr |= a[1]
                gpstart += 2

        if not newComp.attr:
            match = re.compile(RE_NAMED_GROUP).match(self.pattern, gpstart, end)
            if match:
                newComp.groupName = match.group(1)
                self.groupNames.append(newComp.groupName)
                gpstart = match.end(0)

        # register & recurse
        parent.childList.append(newComp)
        self.parseGroup(gpstart, gpend, newComp)
        return endpos + 1

    def _gpTokenProg(self, start, end, parent):
        if self.pattern[start] in PROG_TYPE:
            newComp = ReComponent(start, TYPE_PROG)
            newComp.action = PROG_TYPE[self.pattern[start]]
            parent.childList.append(newComp)
            return start + 1
        else:
            syntaxError(self.pattern,
                        start,
                        'System error, programmed (zero width) character not implemented')

    def _gpTokenBackslash(self, start, end, parent):
        posn = start + 1
        # prog types
        if self.pattern[posn] in PROG_BACKSLASH:
            return self._gpTokenProg(posn, end, parent)

        # backreference
        match = re.compile(RE_B_BACKREFERENCE).match(self.pattern, posn, end)
        if match:
            newComp = ReComponent(start, TYPE_PROG)
            newComp.action = PROG_BACKREFERENCE
            newComp.ref    = int(match.group(0))
            parent.childList.append(newComp)
            return match.end(0)

        # char types
        if self.pattern[posn] in ESCAPE_CHARACTER:
            self._addCharacterToken(ord(ESCAPE_CHARACTER[self.pattern[posn]]),
                                    posn,
                                    self.pattern[start:start + 2],
                                    parent)
            return posn + 1

        return self._commonTokenBackslash(start, end, parent)

    def _commonTokenBackslash(self, start, end, parent):
        posn = start + 1
        #code points
        match = re.compile(RE_CODE_POINT).match(self.pattern, posn, end)
        if match:
            if match.group(1):
                    res     = '0000' + match.group(1)
                    extract = '\\u' + match.group(1)
                    endpos  = match.end(1)
            elif match.group(2):
                    res     = match.group(2)
                    extract = '\\U' + match.group(2)
                    endpos  = match.end(2)
            self._addCharacterToken(int(res, 16), posn, extract, parent)
            return endpos

        #hex bytes
        match = re.compile(RE_HEX_BYTE).match(self.pattern, posn, end)
        if match:
            res    = match.group(1)
            newComp = ReComponent(start, TYPE_HEX)
            newComp.first   = int(res, 16)
            newComp.last    = newComp.first
            newComp.pattern = "\\x" + res
            parent.childList.append(newComp)
            return match.end(1)

        # escaped classes
        if self.pattern[posn] in CLASS_CHARACTER:
            prop = CLASS_CHARACTER[self.pattern[posn]]
            self._addPropertyToken(None, prop, False, start, parent, posn)
            return posn + 1

        # unicode property classes
        match = re.compile(RE_UNICODE_PROPERTY).match(self.pattern, posn, end)
        if match:
            neg = False
            if self.pattern[posn] == 'P':
                neg = True
            if match.group(1):
                self._addPropertyToken(None, match.group(1), neg, start, parent, posn)
            elif match.group(2):
                self._addPropertyToken(None, match.group(2), neg, start, parent, posn)
            elif match.group(3):
                self._addPropertyToken(match.group(3), match.group(4), neg, start, parent, posn)
            return match.end(0)

        # anything else is interpreted as the single following character
        self._addCharacterToken(ord(self.pattern[posn]),
                                    posn,
                                    self.pattern[start + 1],
                                    parent)
        return posn + 1

    def _gpTokenCharacterClass(self, start, end, parent):

        gpstart = start + 1
        newComp = ReComponent(start, TYPE_CLASS)

        # check if negated
        if self.pattern[start + 1] == '^':
            newComp.attr |= AT_NOT
            gpstart += 1

        # first find the matching end bracket, allowing ']' at start
        bktOffset = 1 if self.pattern[gpstart] == ']' else 0
        gpend  = self._findBracketEnd(gpstart + bktOffset, end, '[')
        newComp.pattern = self.pattern[start:gpend + 1]

        parent.childList.append(newComp)
        self._parseClass(gpstart, gpend, newComp)
        return gpend + 1

    def _gpTokenRepeat(self, start, end, parent):
        # repeat token, converts all repeats to (min,max) form

        newComp = ReComponent(start, TYPE_REPEAT)

        # parse complete repeat spec
        for repeatSpec in REPEAT_SPECS:
            match = re.compile(repeatSpec[0]).match(self.pattern, start, end)
            if match:
                newComp.repeatMin = repeatSpec[1] if repeatSpec[1] >= 0 \
                                    else int(match.group(-repeatSpec[1]))
                newComp.repeatMax = repeatSpec[2] if repeatSpec[2] >= 0 \
                                    else int(match.group(-repeatSpec[2]))
                if match.group(repeatSpec[3]) == '?':
                    newComp.attr |= AT_NOTGREEDY
                endpos = match.end(0)
                break

        # if failed, insert as character
        if not hasattr(newComp, 'repeatMin'):
            return self._gpTokenOther(start, end, parent)

        # check/limit loop repeat sizes
        if newComp.repeatMin > VM_COUNT_UNMEASURED:
            parseLog.warning('Counted loop size specified ({:d} limited to {:d}'.format(newComp.repeatMin, VM_COUNT_UNMEASURED - 1))
            newComp.repeatMin = VM_COUNT_UNMEASURED - 1
            newComp.repeatMax = VM_COUNT_UNMEASURED - 1
        if newComp.repeatMax > VM_COUNT_UNMEASURED:
            parseLog.warning('Maximum loop size specified ({:d} limited to {:d}'.format(newComp.repeatMax, VM_COUNT_UNMEASURED - 1))
            newComp.repeatMax = VM_COUNT_UNMEASURED - 1
        if newComp.repeatMin > newComp.repeatMax:
            parseLog.warning('Required repeat bigger than maximum repeat count, will be set to {:d}'.format(newComp.repeatMax))
            newComp.repeatMin = newComp.repeatMax
        parent.childList.append(newComp)
        return endpos

    def _gpTokenDot(self, start, end, parent):
        newComp = ReComponent(start, TYPE_DOT)
        newComp.pattern = '.'
        parent.childList.append(newComp)
        return start + 1

    def _gpTokenRelation(self, start, end, parent):
        newComp = ReComponent(start, TYPE_ALT)
        parent.childList.append(newComp)
        return start + 1

    def _gpTokenOther(self, start, end, parent):
        # a single character
        self._addCharacterToken(ord(self.pattern[start]), start, self.pattern[start], parent)
        return start + 1

    def _gpTokenHash(self, start, end, parent):
        # only applies if verbose
        if not self.verbose:
            return  self._gpTokenOther(start, end, parent)
        # find comment span and return end to skip pattern
        match = re.compile(RE_VERBOSE_COMMENT).match(self.pattern, start, end)
        return match.end()

    def _gpTokenWhiteSpace(self, start, end, parent):
        # ignore if verbose mode
        if self.verbose:
            return start + 1
        # else just use the character
        return  self._gpTokenOther(start, end, parent)

    def _addCharacterToken(self, ordinal, start, charPattern, parent):
        newComp = ReComponent(start, TYPE_CHAR)
        newComp.first   = ordinal
        newComp.last    = ordinal
        newComp.pattern = charPattern
        parent.childList.append(newComp)

    def _addPropertyToken(self, prop, value, negate, start, parent, posn):
        ''' Note that if only one of prop or value is specified, then prop is
        written as a zero length string and value has the keyword. (sometimes
        this will be a binary property and counter intuitive but sometimes a
        unique value and correct!
        '''
        props = getPropertyValueNames(prop, value)
        if props == None:
            syntaxError(self.pattern,
                        posn,
                        'Property/Value not in UCD Property namespace')
        newComp = ReComponent(start, TYPE_PROPERTY)
        newComp.uproperty = props[0]
        if value:
            newComp.uvalue = props[1]
        if negate:
            newComp.attr |= AT_NOT
        # node pattern is normalised where possible
        newComp.pattern    = "{" + props[0] + "=" + props[1] + "}"
        parent.childList.append(newComp)

    def _listIndexOfType(self, childList, typeFilter):
        ''' return a list of indexes of components in the given childList
        that match a given type
        '''
        res     = []
        for i, comp in enumerate(childList):
            if comp.type == typeFilter:
                res.append(i)
        return res

    #*************************************************************
    #    tokenise character class
    #*************************************************************

    def _parseClass(self, start, end, parent):
        ''' Parent is the content of a character class
        '''

        # tokenize the string into components
        posn = start
        while posn < end:
            posn = self.classAction.get(self.pattern[posn],
                                        self._gpTokenOther)(posn, end, parent)

        # now tidy up parse tree
        # join ranges into ranged characters (type char or hex)
        toDo = self._listIndexOfType(parent.childList, TYPE_RANGE)

        # if range is at start or end, ignore
        endChars = []
        if len(toDo) > 0 and toDo[0] == 0:
            endChars.append(0)
            del toDo[0]
        if len(toDo) > 0 and toDo[-1] > (len(parent.childList) - 2):
            endChars.append(toDo[-1])
            del toDo[-1]
        for posn in endChars:
            parent.childList[posn].type    = TYPE_CHAR
            parent.childList[posn].first   = ord('-')
            parent.childList[posn].last    = ord('-')
            parent.childList[posn].pattern = '-'

        # build ranges
        for j in range(len(toDo)):
            newChildList = []
            i = 0
            while i < (len(parent.childList)):
                # 1 before next relation, but compensate for removed entries
                if i == toDo[j] - (j * 2) - 1:
                    if parent.childList[i].type != parent.childList[i + 2].type:
                        syntaxError(self.pattern,
                                    start,
                                    'Syntax error - inconsistent types at ends of range')
                    if parent.childList[i].type == TYPE_CHAR:
                        newComp = ReComponent(parent.childList[i].start, TYPE_CHAR)
                    elif parent.childList[i].type == TYPE_HEX:
                        newComp = ReComponent(parent.childList[i].start, TYPE_HEX)
                    else:
                        syntaxError(self.pattern,
                                    start,
                                    'Syntax error - invalid types for a range')
                    newComp.first   = parent.childList[i].first
                    newComp.last    = parent.childList[i + 2].last
                    newComp.pattern = parent.childList[i].pattern \
                                                        + '-' \
                                                        + parent.childList[i + 2].pattern
                    newChildList.append(newComp)
                    i += 3
                else:
                    newChildList.append(parent.childList[i])
                    i += 1
            parent.childList = newChildList

        # bind sets to relations
        toDo = self._listIndexOfType(parent.childList, TYPE_RELATION)
        if len(toDo) > 0 and (toDo[0] < 1 or toDo[-1] > len(parent.childList) - 2):
            syntaxError(self.pattern,
                        start,
                        'Character set starts or ends with an incomplete relation')

        for j in range(len(toDo)):
            newChildList = []
            i = 0
            while i < (len(parent.childList)):
                # compensate for removed entries
                if i == toDo[j] - (j * 2) - 1:
                    if not (parent.childList[i].type & TYPE_VALID_IN_RELATION):
                        syntaxError(self.pattern,
                                    start,
                                    'Syntax error: Left side of relation is invalid')
                    if not (parent.childList[i + 2].type & TYPE_VALID_IN_RELATION):
                        syntaxError(self.pattern,
                                    start,
                                    'Syntax error: Right side of relation is invalid')

                    parent.childList[i + 1].childList = [parent.childList[i], parent.childList[i + 2]]
                    newChildList.append(parent.childList[i + 1])
                    i += 3
                else:
                    newChildList.append(parent.childList[i])
                    i += 1
            parent.childList = newChildList

    def _clTokenRelation(self, start, end, parent):
        # standard combiners are double
        if self.pattern[start] == self.pattern[start + 1]:
            attr = CLASS_COMBINER[self.pattern[start]]
            if attr == None:  # '||' is valid but unnecessary
                return start + 2
            newComp = ReComponent(start, TYPE_RELATION)
            newComp.attr |= attr
            parent.childList.append(newComp)
            return start + 2

        if self.pattern[start] == '-':
            return self._clTokenRange(start, end, parent)

        # otherwise they are simply standard characters
        self._addCharacterToken(ord(self.pattern[start]),
                            start,
                            self.pattern[start],
                            parent)
        return start + 1

    def _clTokenRange(self, start, end, parent):
        # this just does temp range token, later combined into char or hex range
        newComp = ReComponent(start, TYPE_RANGE)
        parent.childList.append(newComp)
        return start + 1

    def _clTokenBackslash(self, start, end, parent):
        # limited range of characters to escape
        posn = start + 1

        # char types
        if self.pattern[posn] in CLASS_ESCAPE_CHARACTER:
            self._addCharacterToken(ord(CLASS_ESCAPE_CHARACTER[self.pattern[posn]]),
                                    posn,
                                    self.pattern[start: start + 2],
                                    parent)
            return posn + 1

        return self._commonTokenBackslash(start, end, parent)

    def _findBracketEnd(self, start, end, b_open):
        ''' find a matching end bracket, bypassing nested BRACKETS
        '''
        b_close = BRACKETS[b_open][0]
        endpos = start
        bracketCount = 0
        while endpos < end:
            tst = self.pattern[endpos]
            if tst  == '\\':
                # skip chars after backslash
                endpos += 1
            elif tst == b_open:
                # increment nested count
                bracketCount += 1
            elif tst == b_close:
                if bracketCount == 0:
                    break
                bracketCount -= 1
            elif tst in BRACKETS[b_open][1]:
                # skip past a different bracket type
                endpos = self._findBracketEnd(endpos + 1, end, tst)
            endpos += 1
        if endpos >= end:
            syntaxError(self.pattern,
                        start,
                        'Syntax error: bracket {}{} not closed'.format(b_open, b_close))
        return endpos

    def _checkIfGroupLazy(self, comp):
        ''' check if any quantifiers within the group are marked as
        non-greedy and if so mark the group as non-greedy.
        If quantifiers are inconsistent (mixed greedy and lazy)
        within the span of a single group a syntax error is thrown.

        comp is a group to be tested.
        '''

        # if group has been annotated as lazy manually, this overrides quantifiers
        if comp.attr & AT_NOTGREEDY:
            return

        greedy = False
        lazy   = False
        for child in comp.childList:
            if child.type == TYPE_REPEAT:
                if child.attr & AT_NOTGREEDY:
                    lazy = True
                else:
                    greedy = True
        if greedy and lazy:
            syntaxError(self.pattern,
                        comp.start,
                        'Group or alt branch contains both greedy and lazy (reluctant) quantifiers')
        if lazy:
            comp.attr |= AT_NOTGREEDY


def syntaxError(pattern, posn, msg):
    parseLog.error(pattern)
    parseLog.error(' ' * posn + '^')
    parseLog.error(msg + ' at {:d}'.format(posn))
    raise SyntaxError(msg + ' at {:d}'.format(posn))

#***********************************************************************
#      ReComponent Tree
#************************************************************************
StackEntry = namedtuple('StackEntry', ('comp', 'posn'))


class ReComponent():
    ''' Any part of an re, forms a parse tree.

    Class Methods
        iterator    (__next__ etc) over whole (sub) tree
                    is tolerant to modifications to current
                    object or any of its subtree
                    returns a tuple (depth, ReComponent)
        update      modify node type
        clone
        print       prints whole (sub)tree
    '''

    def __init__(self, start, cType):
        '''
        Params
        start    start position in re, mostly used to report error positions
        ctype    the node type
        '''

        self.type    = cType      # the type of the component
        self.start   = start      # start position in re (for error reporting)
        self.attr    = 0
        if cType & TYPE_HAS_CHILD:
            self.childList = []

    def update(self, ctype, ref):
        ''' modify the type of this node
            ref is assigned to self.ref
            delete or create childList as appropriate
            attr and other attributes are not modified
        '''
        if hasattr(self, 'childList'):
            del self.childList
        self.type = ctype
        self.ref  = ref
        if ctype & TYPE_HAS_CHILD:
            self.childList = []

    def filteredBy(self, typeFilter):
        '''
        returns an iterator which will iterate over the subtree of self,
        returning only components of the specified type
        '''
        return _filteredTree(self, typeFilter)

    def __iter__(self):
        '''
        This iterator is child-modify-safe, in other words if a child node
        is modified/added/removed the iterator will correctly continue with
        the new tree.

        Iteration is left-depth first - ie normal execution order of re.
        '''
        if not hasattr(self, 'stack_comp'):
            self.stack_comp = [None] * MAX_TREE_DEPTH
            self.stack_posn = [None] * MAX_TREE_DEPTH
        self.sp      = 0
        self.first   = True
        return self

    def __next__(self):
        sp = self.sp
        if self.first:
            self.stack_comp[sp] = self
            self.stack_posn[sp] = None
            self.first = False
            return (sp, self)

        if self.stack_posn[sp] == None:
            #last entry was this node for the first time
            comp = self.stack_comp[sp]
            if hasattr(comp, 'childList'):
                # Process children
                self.stack_comp[sp] = comp
                self.stack_posn[sp] = 0
                posn                = 0
            else:
                # pop stack
                while True:
                    if sp == 0:
                        raise StopIteration
                    sp -= 1
                    posn = self.stack_posn[sp] + 1
                    comp = self.stack_comp[sp]
                    if posn < len(comp.childList):
                        # found next entry
                        break
                self.stack_comp[sp] = comp
                self.stack_posn[sp] = posn

            # push stack
            sp += 1
            if sp >= MAX_TREE_DEPTH:
                msg = 'Stack overflow while processing tree, recursion too deep'
                parseLog.error(msg)
                raise SyntaxError(msg)
            comp = comp.childList[posn]
            self.stack_comp[sp] = comp
            self.stack_posn[sp] = None
            self.sp             = sp
            return (sp, comp)
        else:
            # here probably means that there has been a call to iterator while another is running
            raise SystemError('Tree iterator stack is corrupt.')

    def clone(self):
        ''' Return a clone of a parse tree
        '''
        parent = [None] * MAX_TREE_DEPTH
        for depth, comp in self:
            #clone component record
            newComp = copy.copy(comp)
            newComp.attr = comp.attr

            if hasattr(newComp, 'childList'):
                # remember parent for children
                newComp.childList = []
                parent[depth + 1] = newComp
            #put in tree
            if depth == 0:
                newRoot = newComp
            else:
                parent[depth].childList.append(newComp)
        return newRoot

    def print(self):
        print('********** Parse Tree **********')
        for depth, comp in self:
            typename = '{:d}:'.format(comp.start) + TYPE_LOOKUP[comp.type]
            extra = '     '
            if comp.attr & AT_NOT:
                extra  = ' NOT '
            if hasattr(comp, 'pattern'):
                extra += comp.pattern + '\t'
            if comp.type == TYPE_CHAR or comp.type == TYPE_HEX:
                extra += '({:4x},{:4x})'.format(comp.first, comp.last)
            elif comp.type == TYPE_REPEAT:
                extra += ' {{{:d},{:d}}}'.format(comp.repeatMin, comp.repeatMax)
                if comp.attr:
                    extra += ' ' + ATTRIBUTE_LOOKUP[comp.attr]
            elif comp.type == TYPE_PROG:
                extra += ACTION_LOOKUP[comp.action]
            elif comp.type == TYPE_GROUP:
                for s in GROUP_SIGNATURES:
                    if comp.attr & s[1]:
                        extra += ATTRIBUTE_LOOKUP[s[1]] + ' '
                if hasattr(comp, 'groupName'):
                    extra += 'name:' + comp.groupName
            elif comp.type == TYPE_RELATION:
                if comp.attr & AT_COMBINE_AND:
                    extra += "and"
                else:
                    extra += "difference"
            if hasattr(comp, 'ref') and comp.type == TYPE_COMPILED:
                extra += " ref({:d}) ".format(comp.ref)
            print(('  ' * depth) + typename + extra)
        print("********************************")


class _filteredTree():
    '''
    tree iterator filtered by node type
    returns only ReComponents, not tuples with depth
    '''
    def __init__(self, tree, typeFilter):
        self.root = tree
        self.typeFilter = typeFilter

    def __iter__(self):
        self.root.__iter__()
        return self

    def __next__(self):
        while True:
            comp = self.root.__next__()
            if comp[1].type & self.typeFilter:
                return comp[1]
