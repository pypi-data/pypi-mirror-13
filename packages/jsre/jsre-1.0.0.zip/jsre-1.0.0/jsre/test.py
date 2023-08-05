'''
Unit and system tests for jsre.

@author: Howard Chivers

Copyright (c) 2015, Howard Chivers
All rights reserved.

'''
import unittest
import os
import logging
import re
from jsvm import Jsvm
import pickle

import jsre
from jsre.reobjects import _getModuleCache
from jsre.ucd import isEncodingInstalled, UCDTestCases
from jsre.ucd import getClassPath, getPropertyValueNames, compileEncoding, normaliseName
from jsre.charclass import CharClass, _equalRanges, newCasedCharacter, newClassFromList
from jsre.charclass import _intersectRangesWithValues, Range, _normaliseRanges
from jsre.reparser import parseRE, VERBOSE, IGNORECASE
from jsre.dfacompiler import CharacterCompiler

from jsre.reparser import PROG_TEXT_START, PROG_TEXT_END, PROG_BUFF_START, PROG_BUFF_END, PROG_WBOUNDARY, PROG_NWBOUNDARY
from jsre.reparser import TYPE_GROUP, TYPE_CLASS, TYPE_CHAR, TYPE_ALT, TYPE_REPEAT, TYPE_RELATION, AT_NOT, TYPE_COMPILED, TYPE_PROG, TYPE_CHARCLASS, TYPE_CLASSREF
from jsre.reparser import AT_NOTGREEDY, AT_NOTCONSUME, AT_NOTCAPTURE, VM_COUNT_UNMEASURED

testLog = logging.getLogger("unit test")

# VM Instruction Set
VM_CHARACTER_OK            = 0xFFFF    # character transition success

VM_INSTR_CHARACTER         =   0x20    # a character [group], if set then ...
VM_INSTR_NEW_THREAD        =   0x1     # write temp state to new thread
VM_INSTR_PUBLISH           =   0x4     # publish (write marked locations to result)
VM_INSTR_MARK_START        =   0xA     # mark start of re or subgroup
VM_INSTR_MARK_END          =   0xE     # write current byte address to indexed mark

TEST_REFERENCE   = 'reference'
TEST_IMAGES      = 'images'
RE_TESTS         = 'Test_Expressions.txt'
TEST_ROOT        = 'JSRE_Test'             # must be in UCD header file as name
DEV_TEST_ROOT    = 'JSRE_dev_Test'         # for large reference file system tests
ATT_TESTS        = 'Test_ATT_Regression.txt'    # Reference AT&T RE regression tests
TEST_BUFFER_SIZE = 1048576
RE_NOTASCIIPRINT = '[^ -~]'


class Test_basicCharacters(unittest.TestCase):
    #
    # test basic character class build and logic in utf-8
    # primitive set operations are redundant so are checked against each other
    #

    def setUp(self):
        # compile test cases
        self.encoding = 'UTF-8'
        self.testFileA = getClassPath(self.encoding, *getPropertyValueNames(None, 'test_a'))
        self.testFileB = getClassPath(self.encoding, *getPropertyValueNames(None, 'test_b'))

    def test_equals(self):
        # testing depends on all this
        print('Class Equals')
        tc = CharClass('ascii')
        tc.transitions = {0: {20: 1, 21: 2}, 2: {22: 3}, 1: {22: 4}}
        tc.leafs       = {3: [Range(5, 6)], 4: [Range(7, 8)]}
        tc.stateSize   = 5
        rc = CharClass('ascii')
        rc.transitions = {0: {20: 2, 21: 1}, 2: {22: 3}, 1: {22: 4}}
        rc.leafs       = {3: [Range(7, 8)], 4: [Range(5, 6)]}
        rc.stateSize   = 5
        xc = rc.clone()
        self.assertTrue(tc.equals(tc), msg='Class Equals - 1  - Same object')
        self.assertTrue(tc.equals(rc), msg='Class Equals - 2 - Same data')
        rc.stateSize   = 4
        self.assertFalse(tc.equals(rc), msg='Class Equals - 3 - Size mismatch')
        rc = xc.clone()
        rc.encoding = 'utf_8'
        self.assertFalse(tc.equals(rc), msg='Class Equals - 4 - Encoding mismatch')
        rc = xc.clone()
        rc.leafs[0] = [Range(0, 1)]
        self.assertFalse(tc.equals(rc), msg='Class Equals - 5 - Number of leafs mismatch')
        rc = xc.clone()
        rc.transitions[4] = {22: 5}
        self.assertFalse(tc.equals(rc), msg='Class Equals - 6 - Number of transitions mismatch')
        rc = xc.clone()
        rc.transitions[2] = {99: 3}
        self.assertFalse(tc.equals(rc), msg='Class Equals - 7 - Transition Key mismatch')
        rc = xc.clone()
        rc.leafs       = {3: [Range(7, 8)], 2: [Range(5, 6)]}
        self.assertFalse(tc.equals(rc), msg='Class Equals - 8 - Leaf Key mismatch')
        rc = xc.clone()
        rc.leafs[3] = Range(99, 100)
        self.assertFalse(tc.equals(rc), msg='Class Equals - 9 - Range mismatch')

    def test_encodings(self):
        ENCODINGS  = ['UTF-8', 'UTF-16-BE', 'UTF-32-BE']
        TEST_PAIRS = [('Alphabetic', 'Latin'),
                      ('Lowercase', 'Coptic'),
                      ('Ps', 'Common'),
                      ('Lowercase', 'Uppercase'),
                      ('Alphabetic', 'Alphabetic'),
                      ('Digit', 'Punctuation')]

        for e in ENCODINGS:
            for p in TEST_PAIRS:
                msg = "Encoding {} with character classes: {}: ".format(e, str(p))
                print(msg)
                for t in [unionTest, intersectTest, differenceTest]:
                    cc = CharClass(e)
                    cr = CharClass(e)
                    # note - following unprotected so none path will raise
                    cc.loadFromFile(getClassPath(e, *getPropertyValueNames(None, p[0])))
                    cr.loadFromFile(getClassPath(e, *getPropertyValueNames(None, p[1])))
                    self.assertTrue(t(cc, cr), msg=msg)

    def test_multiCharacter(self):
        print('Multi character sequence')
        cc = newCasedCharacter(None, 'ascii', '\r\n', False)
        self.assertEqual(cc.getStateSize(), 2, msg='Multicharacter sequence state length')

    def test_silentMissingFileLoad(self):
        print('Missing file silent in character load')
        cc = newClassFromList('ascii', ('notafilepath',))
        self.assertEqual(cc.getStateSize(), 0, msg='Missing file silent in character load')

    def test_nondeterministic(self):
        print('Nondeterministic detection')
        cc = newCasedCharacter(None, 'ascii', 'abc', True)
        cr = newCasedCharacter(None, 'ascii', 'ab', True)
        cr.union(cc)
        states = cr._mapNondeterministicStates()
        self.assertEqual(states[1][0], 98, msg='Nondeterministic detection')

    def test_SequenceWithEmptyCC(self):
        print('Sequence with empty class')
        cc = newCasedCharacter(None, 'ascii', 'abc', True)
        cr = CharClass('ascii')
        ct = cc.clone()
        ct.addAsSequence(cr)
        self.assertEqual(ct.equals(cc), True, msg='Sequence with right empty class')
        cr.addAsSequence(ct)
        self.assertEqual(cr.equals(cc), True, msg='Sequence with left empty class')

    def test_opsIdenticalObjects(self):
        print('Set operations on identical objects')
        cr = newCasedCharacter(None, 'ascii', 'ab', True)
        cc = cr.clone()
        cc.difference(cc)
        self.assertEqual(cc.isEmpty(), True, msg='Difference identical objects')
        cc = cr.clone()
        cc.union(cc)
        self.assertEqual(cc.equals(cr), True, msg='Union identical objects')
        cc.intersect(cc)
        self.assertEqual(cc.equals(cr), True, msg='Intersect identical objects')

    def test_rangeAndValue(self):
        print('Intersect range with values')
        r1   = (Range(0, 10), Range(20, 20), Range(99, 100))
        v1   = (0, 5, 10, 19, 20, 21, 98, 101)
        test = [0, 5, 10, 20]
        self.assertEqual(_intersectRangesWithValues(r1, v1), test, msg='Intersect range with values')
        self.assertEqual(_intersectRangesWithValues(r1, ()), [], msg='Intersect range with empty values')

    def test_normaliseRange(self):
        print('Normalise Range')
        r1   = [Range(0, 10), Range(20, 20), Range(99, 100), Range(1, 3), Range(11, 11), Range(89, 89)]
        test = [Range(0, 11), Range(20, 20), Range(89, 89), Range(99, 100)]
        self.assertEqual(_normaliseRanges(r1), test, msg='Normalise Range')
        r1   = [Range(1, 10)]
        test = [Range(1, 10)]
        self.assertEqual(_normaliseRanges(r1), test, msg='Normalise Short Range')

    def test_testOrRemoveStates(self):
        print('Test or Remove State')
        tc = CharClass('ascii')
        tc.transitions = {0: {20: 1, 21: 2}, 2: {22: 3}}
        tc.leafs       = {2: ()}
        test = {0: {20: 1, 21: 2}, 2: {22: 3}}
        tc.leafs[1] = [Range(80, 99)]
        tc.stateSize = 4
        imap = {3: (2, 22), 2: (0, 21), 1: (0, 20)}
        tc._testOrRemoveState(1, imap)
        self.assertEqual(tc.transitions, test, msg='Test or Remove State - 1 - state used')
        tc._testOrRemoveState(5, imap)
        self.assertEqual(tc.transitions, test, msg='Test or Remove State - 2 - state not in transitions')
        test = {0: {20: 1}}
        tc._testOrRemoveState(3, imap)
        self.assertEqual(tc.transitions, test, msg='Test or Remove State - 3 - remove state and tansitions')
        tc._testOrRemoveState(3, imap)
        self.assertEqual(tc.transitions, test, msg='Test or Remove State - 4 - state proviously removed')
        tc.transitions = {0: {20: 1, 99: 2}}
        test = {0: {99: 2, 20: 1}}
        tc._testOrRemoveState(2, imap)
        self.assertEqual(tc.transitions, test, msg='Test or Remove State - 5 - imap tranistion inconsistent')
        tc.transitions = {0: {20: 1}}
        test = {}
        del(tc.leafs[1])
        tc._testOrRemoveState(1, imap)
        self.assertEqual(tc.transitions, test, msg='Test or Remove State - 6 - remove root')

    def test_joinStates(self):
        print('Join States')
        tc = CharClass('ascii')
        tc.transitions = {0: {20: 1, 21: 2}, 2: {22: 3}, 1: {22: 4}}
        tc.leafs       = {3: [Range(5, 6)], 4: [Range(5, 6)]}
        tc.stateSize   = 5
        rc             = tc.clone()
        imap           = {1: (0, 20), 2: (0, 21), 3: (2, 22), 4: (1, 22)}
        testt = {0: {20: 2, 21: 2}, 2: {22: 3}}
        testl = {3: [Range(5, 6)]}
        tc._joinStates(imap, 3, 4)
        self.assertEqual(tc.transitions, testt, msg='Join States - 1 - Normal')
        self.assertEqual(tc.leafs, testl, msg='Join States - 2 - Normal')

        tc = rc.clone()
        tc.leafs[2] = [Range(10, 11)]
        tc._joinStates(imap, 3, 4)
        testt = {0: {20: 1, 21: 2}, 1: {22: 3}, 2: {22: 3}}
        testl = {2: [Range(10, 11)], 3: [Range(5, 6)]}
        self.assertEqual(tc.transitions, testt, msg='Join States - 3 - Block Left')
        self.assertEqual(tc.leafs, testl, msg='Join States - 4 - Block Left')

        tc = rc.clone()
        tc.leafs[1] = [Range(10, 11)]
        tc._joinStates(imap, 3, 4)
        testl = {1: [Range(10, 11)], 3: [Range(5, 6)]}
        self.assertEqual(tc.transitions, testt, msg='Join States - 5 - Block Right')
        self.assertEqual(tc.leafs, testl, msg='Join States - 6 - Block Right')

        tc = rc.clone()
        tc.leafs       = {1: [Range(12, 13)], 2: [Range(10, 11)], 3: [Range(5, 6)], 4: [Range(5, 6)]}
        tc._joinStates(imap, 3, 4)
        testl = {1: [Range(12, 13)], 2: [Range(10, 11)], 3: [Range(5, 6)]}
        self.assertEqual(tc.transitions, testt, msg='Join States - 7 - Range Mismatch')
        self.assertEqual(tc.leafs, testl, msg='Join States - 8 - Range Mismatch')

        tc = rc.clone()
        tc.transitions[1] = {22: 4, 99: 5}
        tc.stateSize      = 6
        tc._joinStates(imap, 3, 4)
        testt = {0: {20: 1, 21: 2}, 1: {99: 5, 22: 3}, 2: {22: 3}}
        testl = {3: [Range(5, 6)]}
        self.assertEqual(tc.transitions, testt, msg='Join States - 9 - Transition Mismatch')
        self.assertEqual(tc.leafs, testl, msg='Join States - 10 - Transition Mismatch')

    def test_byteRange(self):
        print('Byte Ranges')
        tc = CharClass('ascii')
        tc.loadByteRange(55, 60)
        test = {0: [Range(55, 60)]}
        self.assertEqual(tc.leafs, test, msg='Byte Range - 1 - Initial leaf')
        tc.loadByteRange(59, 65)
        test = {0: [Range(55, 65)]}
        self.assertEqual(tc.leafs, test, msg='Byte Range - 2 - add to leaf')


class Test_jsvm(unittest.TestCase):
    #
    # Basic test of jsvm wrapper,
    # main unit tests for jsvm are in the c test code.
    #

    def test_search(self):
        print("JVSM wrapper")

        test_fm_trans       = (b"a", b"b", b"n", b"o", b"xX", b"pq")

        test_fm_prog = (  # (instruction.index,address,last)
        (
            (VM_INSTR_MARK_END, 0, 0, False),
            (VM_INSTR_PUBLISH, 0, 0, True)
        ), (
            (VM_INSTR_NEW_THREAD, 0, 0, False),
            (VM_INSTR_CHARACTER, 0, 0, False),
            (VM_INSTR_NEW_THREAD, 0, 0, True)
        ), (
            (VM_INSTR_NEW_THREAD, 0, 1, False),
            (VM_INSTR_CHARACTER, 0, 0, False),
            (VM_INSTR_NEW_THREAD, 0, 1, True)
        ), (
            (VM_INSTR_NEW_THREAD, 0, 2, False),
            (VM_INSTR_CHARACTER, 0, 5, False),
            (VM_INSTR_NEW_THREAD, 0, 2, True)
        ), (
            (VM_INSTR_MARK_START, 0, 0, False),       # RE4 = ab[xX]a[xX][pq](0,1)a(0,1)a(0,1)
            (VM_INSTR_CHARACTER, 0, 0, False),
            (VM_INSTR_CHARACTER, 0, 1, False),
            (VM_INSTR_CHARACTER, 0, 4, False),
            (VM_INSTR_CHARACTER, 0, 0, False),
            (VM_INSTR_CHARACTER, 0, 4, False),
            (VM_INSTR_NEW_THREAD, 0, 3, True)
        ), (
            (VM_INSTR_MARK_START, 0, 0, False),       # RE5 = ano
            (VM_INSTR_CHARACTER, 0, 0, False),
            (VM_INSTR_CHARACTER, 0, 2, False),
            (VM_INSTR_CHARACTER, 0, 3, False),
            (VM_INSTR_MARK_END, 0, 0, False),
            (VM_INSTR_PUBLISH, 0, 0, True)
        ))

        test_fm_start   = ((0, 4), (0, 5))  # (command, program index,ret count,offset,stride)

        test_fm_buffer0 = b"absgaaanyanobabxaXatyvohutabXaxqzgyabxaxaaaaaahubsuond"

        ref_result  =       [(13, 19), (26, 32), (35, 42), (9, 12)]

        resultCount = 0
        tvm = getRawVM(test_fm_trans, test_fm_prog, test_fm_start)
        res = tvm.findMatch(test_fm_buffer0, 0, len(test_fm_buffer0), len(test_fm_buffer0), False)

        for i in range(len(res)):
            resultCount += 1
            self.assertEqual(res[i][1], ref_result[i], msg='Jvsm Wrapper {:d}'.format(i))

        self.assertEqual(resultCount, 4, msg='Jvsm wrapper result count')

        # unload and reload in new object and try again

        state = tvm.__getstate__()
        tvm = Jsvm()
        tvm.__setstate__(state)

        res = tvm.findMatch(test_fm_buffer0, 0, len(test_fm_buffer0), len(test_fm_buffer0), False)

        resultCount = 0
        for i in range(len(res)):
            resultCount += 1
            self.assertEqual(res[i][1], ref_result[i], msg='Jvsm get-set state in wrapper{:d}'.format(i))

        self.assertEqual(resultCount, 4, msg='Jvsm get-set state in wrapper result count')

        # repeat using pickle

        state = pickle.dumps(tvm)
        tvm = None
        tvm = pickle.loads(state)

        res = tvm.findMatch(test_fm_buffer0, 0, len(test_fm_buffer0), len(test_fm_buffer0), False)

        resultCount = 0
        for i in range(len(res)):
            resultCount += 1
            self.assertEqual(res[i][1], ref_result[i], msg='Jvsm get-set state in wrapper{:d}'.format(i))

        self.assertEqual(resultCount, 4, msg='Jvsm pickle state in wrapper result count')

    def test_pickle(self):
        print('serialise regex object')
        pattern = '\w+'
        buffer1 = b'quick brown fox'
        buffer2 = b'jumps again'
        ref   = ['quick', 'brown', 'fox', 'jumps', 'again']

        regex = jsre.compile(pattern)

        state = regex._tvm.__getstate__()
        regex._tvm = Jsvm()
        regex._tvm.__setstate__(state)
        res = []
        for match in regex.finditer(buffer1):
            res.append(match.group())

        state = pickle.dumps(regex)
        rtst = pickle.loads(state)
        for match in rtst.finditer(buffer2):
            res.append(match.group())

        self.assertEqual(ref, res, msg="serialise regex opject, result = {}".format(str(res)))


class Test_tokens(unittest.TestCase):
    #
    # tokeniser
    #
    def test_characterTokens(self):
        print('Tokeniser - character class values')
        pattern = r'a\a\f\n\r\t\u1234\U0010F00E\v\xcd\\\"'
        ref     = (0x61, 0x7, 0xC, 0xA, 0xD, 0x9, 0x1234, 0x0010F00E, 0xb, 0xcd, 0x5c, 0x22)
        root = parseRE(pattern, False)
        root = root.clone()  # this just to test clone at the same time
        for i in range(len(ref)):
            self.assertEqual(ref[i], root.childList[i].first, msg='Tokeniser - character class values, index{:d}'.format(i))

    def test_zeroWidth(self):
        print('Tokeniser - zerowidth programs')
        pattern = r'^$\A\z\b\B'
        ref     = (PROG_TEXT_START, PROG_TEXT_END, PROG_BUFF_START, PROG_BUFF_END, PROG_WBOUNDARY, PROG_NWBOUNDARY)
        root = parseRE(pattern, False)
        root = root.clone()
        for i in range(len(ref)):
            self.assertEqual(ref[i], root.childList[i].action, msg='Tokeniser - zerowidth programs, index {:d}'.format(i))

    def test_characterSetElements(self):
        print("Tokeniser - character set elements")
        pattern = r'[ab-c\x10-\x20.\d\s\w\pS\p{word}\p{line-Break = glue}\D\S\W\PS\P{cased}\P{script:latin}]'
        ref0 = ((0x61, 0x61), (0x62, 0x63), (0x10, 0x20))
        ref1 = (('general_category', 'decimal_number'), ('', 'blank'), ('', 'word'), ('general_category', 'symbol'), ('', 'word'), ('line_break', 'glue'), ('', 'not_digit'), ('', 'not_blank'), ('', 'not_word'), ('general_category', 'symbol'), ('', 'cased'), ('script', 'latin'))
        ref2 = (0, 0, 0, 0, 0, 0, 0, 0, 0, AT_NOT, AT_NOT, AT_NOT)
        root = parseRE(pattern, False)
        root = root.clone()

        childlist = root.childList[0].childList
        for i in range(len(ref0)):
            self.assertEqual(ref0[i][0], childlist[i].first, msg='Tokeniser, first character index {:d}'.format(i))
            self.assertEqual(ref0[i][1], childlist[i].last, msg='Tokeniser, last character index {:d}'.format(i))
        self.assertEqual(childlist[3].type, TYPE_CHAR, msg='Tokeniser - dot is char in class')
        for i in range(len(ref1)):
            self.assertEqual(ref1[i][0], childlist[i + 4].uproperty, msg='Tokeniser, property index {:d}'.format(i))
            self.assertEqual(ref1[i][1], childlist[i + 4].uvalue, msg='Tokeniser, value index {:d}'.format(i))
            self.assertEqual(ref2[i], AT_NOT & childlist[i + 4].attr, msg='Tokeniser, attr index {:d}'.format(i))

    def test_characterSetRelations(self):
        print("Tokeniser - character set relations")
        pattern = r'[a||b[^cd]&&[[e]&&[f]]--gh]'
        ref0    = (0x61, 0x62, 0x63, 0x64, 0x65, 0x66, 0x67, 0x68)
        ref1    = (TYPE_GROUP, TYPE_CLASS, TYPE_CHAR, TYPE_CHAR, TYPE_RELATION, TYPE_RELATION, TYPE_CLASS, TYPE_CHAR, TYPE_CHAR, TYPE_CLASS, TYPE_RELATION, TYPE_CLASS, TYPE_CHAR, TYPE_CLASS, TYPE_CHAR, TYPE_CHAR, TYPE_CHAR)
        root = parseRE(pattern, False)
        root = root.clone()
        j = 0
        for i, comp in enumerate(root):
            self.assertEqual(ref1[i], comp[1].type, msg='Tokeniser, relation type - index {:d}'.format(i))
            if ref1[i] == TYPE_CHAR:
                self.assertEqual(ref0[j], comp[1].first, msg='Tokeniser, relation first - index {:d}'.format(i))
                j += 1
            if i == 6:
                self.assertEqual(AT_NOT, AT_NOT & comp[1].attr, msg='Tokeniser, relation not - index {:d}'.format(i))

    def test_scanPrefix(self):
        print("Scan Prefix")
        patterns = ('abcdef',
                    '(?=abcd)',
                    'abc|pqr',
                    'x*pqrs',
                    'a*',
                    'x{3,4}',
                    'ab(cd)ef',
                    'abc(?=pqr)def',
                    'a(pq|rst)bcdef',
                    'abc(x*)def',
                    'ax{3,5}bcdef',
                    'a(?=p(?=xy)qrs)bcdef',
                    'abc|p(x|y)qrts',
                    'abc|(?=pqr)xy',
                    'ab|cdx*ef',
                    'pqrstu|cdx*ef',
                    'pqrstu|x{4,6}ef',
                    '(a(?=pq)b)*',
                    '(a(?=pq)b){2,3}',
                    '(ab|cde){2,3}',
                    '(ax{1,3}b){2,3}'
                    )
        test    = (('a', 'b', 'c', 'd', 'e', 'f'),
                    None,
                    ('ap', 'bq', 'cr'),
                    ('xp', 'xpq', 'xpqr', 'xpqrs'),
                    None,
                    ('x', 'x', 'x'),
                    ('a', 'b', 'c', 'd', 'e', 'f'),
                    ('a', 'b', 'c', 'pd', 'qe', 'rf'),
                    ('a', 'pr', 'qs', 'tb', 'cb', 'dc'),
                    ('a', 'b', 'c', 'xd', 'xed', 'xdef'),
                    ('a', 'x', 'x', 'x', 'xb', 'xbc'),
                    ('a', 'bp', 'cqx', 'dry', 'es', 'f'),
                    ('ap', 'bxy', 'cq'),
                    ('apx', 'bqy'),
                    ('ac', 'bd'),
                    ('pc', 'qd', 'rxe', 'sxef'),
                    ('px', 'qx', 'rx', 'sx', 'txe', 'uxef'),
                    None,
                    ('a', 'bp', 'aq', 'bp'),
                    ('ac', 'bd', 'aec', 'abcd'),
                    ('a', 'x', 'xb', 'xba', 'bxa', 'xba'))
        for i, pt in enumerate(patterns):
            if not testPrefix(pt, test[i]):
                self.assertTrue(testPrefix(pt, test[i]), msg='Scan Prefix error, pattern = {}'.format(pt))

    def test_grouping(self):
        print("Tokeniser - grouping")
        pattern = r'a(??bc)(?#comment)d(?=e)(?:f)(?P<eric>(g))'
        ref0    = (0x61, 0x62, 0x63, 0x64, 0x65, 0x66, 0x67)
        ref1    = (TYPE_GROUP, TYPE_CHAR, TYPE_GROUP, TYPE_CHAR, TYPE_CHAR, TYPE_CHAR, TYPE_GROUP, TYPE_CHAR, TYPE_GROUP, TYPE_CHAR, TYPE_GROUP, TYPE_GROUP, TYPE_CHAR)
        ref2    = (None, AT_NOTGREEDY, AT_NOTCONSUME, AT_NOTCAPTURE, None, None)
        root = parseRE(pattern, False)
        root = root.clone()
        j = 0
        k = 0
        for i, comp in enumerate(root):
            self.assertEqual(ref1[i], comp[1].type, msg='Tokeniser, grouping type - index {:d}'.format(i))
            if ref1[i] == TYPE_CHAR:
                self.assertEqual(ref0[j], comp[1].first, msg='Tokeniser, grouping first - index {:d}'.format(i))
                j += 1
            if ref1[i] == TYPE_GROUP:
                if ref2[k] != None:
                    self.assertTrue(ref2[k] & comp[1].attr, msg='Tokeniser, grouping attr - index {:d}'.format(i))
                if k == 4:
                    self.assertEqual('eric', comp[1].groupName, msg='Tokeniser, grouping name - index {:d}'.format(i))
                k += 1

    def test_repeats(self):
        print("Tokeniser - repeats")
        pattern = r'a*b?c+d{5}e{6,7}|fg'
        ref0    = (0x61, 0x62, 0x63, 0x64, 0x65, 0x66, 0x67)
        ref1    = (TYPE_GROUP, TYPE_ALT, TYPE_GROUP, TYPE_REPEAT, TYPE_CHAR, TYPE_REPEAT, TYPE_CHAR, TYPE_REPEAT, TYPE_CHAR, TYPE_REPEAT, TYPE_CHAR, TYPE_REPEAT, TYPE_CHAR, TYPE_GROUP, TYPE_CHAR, TYPE_CHAR)
        ref2    = ((0, VM_COUNT_UNMEASURED), (0, 1), (1, VM_COUNT_UNMEASURED), (5, 5), (6, 7))
        root = parseRE(pattern, False)
        root = root.clone()
        j = 0
        k = 0
        for i, comp in enumerate(root):
            self.assertEqual(ref1[i], comp[1].type, msg='Tokeniser, repeat type - index {:d}'.format(i))
            if ref1[i] == TYPE_CHAR:
                self.assertEqual(ref0[j], comp[1].first, msg='Tokeniser, repeat first - index {:d}'.format(i))
                j += 1
            if ref1[i] == TYPE_REPEAT:
                self.assertEqual(ref2[k][0], comp[1].repeatMin, msg='Tokeniser, repeat min - index {:d}'.format(i))
                self.assertEqual(ref2[k][1], comp[1].repeatMax, msg='Tokeniser, repeat max - index {:d}'.format(i))
                k += 1

    def test_lazy_repeats(self):
        print("Tokeniser - lazy repeats")
        pattern = r'a??b+?c*?e{2}?f{,3}?g{4,5}?'
        ref     = (AT_NOTGREEDY, AT_NOTGREEDY, AT_NOTGREEDY, AT_NOTGREEDY, AT_NOTGREEDY, AT_NOTGREEDY)
        root = parseRE(pattern, False)
        for i in range(len(ref)):
            self.assertEqual(ref[i], root.childList[i].attr, msg='Tokeniser - lazy repeat at {:d}'.format(i))

    def test_groupPromotion(self):
        print('Test Group Promotion')
        pattern = r'(??ab|cd)'
        ref1    = (TYPE_GROUP, TYPE_GROUP, TYPE_ALT, TYPE_GROUP, TYPE_CHAR, TYPE_CHAR, TYPE_GROUP, TYPE_CHAR, TYPE_CHAR)

        root = parseRE(pattern, False)
        for i, comp in enumerate(root):
            self.assertEqual(ref1[i], comp[1].type, msg='Group promotion type - index {:d}'.format(i))

    def test_publisher(self):
        print("Character class publisher")
        pattern = r'a\p{word}b.c\p{script:han}d\We\P{alpha}'   # character classes only
        testLen = 5
        root = parseRE(pattern, False)
        tvm = Jsvm()
        ccompiler = CharacterCompiler(tvm)
        tref = ccompiler.compileCharacters(root, 'utf_8', 0, doNotPublish=True)
        gref = ccompiler.compileCharacters(root, 'utf_8', 0)
        for i in range(testLen):
            self.assertTrue(_testGraphEquals(tref.childList[i].ref, gref.childList[i].ref), msg='Publish - index {:d}'.format(i))

    def test_publisher_little(self):
        print("Character class publisher - little endian")
        pattern = r'a\p{word}b.c\p{script:han}d\We\P{alpha}'  # character classes only
        testLen = 5
        root = parseRE(pattern, False)
        tvm = Jsvm()
        ccompiler = CharacterCompiler(tvm)
        tref = ccompiler.compileCharacters(root, 'utf_16_be', 0, doNotPublish=True)
        gref = ccompiler.compileCharacters(root, 'utf_16_be', 0)
        for i in range(testLen):
            self.assertTrue(_testGraphEquals(tref.childList[i].ref, gref.childList[i].ref), msg='Publish little endian - index {:d}'.format(i))

    def test_cachedVMRefs(self):
        print("Re-use of character DFAs in VM")
        pattern = r'\p{word}.\p{script:han}\W\P{alpha}'
        testLen = 5
        root = parseRE(pattern, False)
        tvm = Jsvm()
        ccompiler = CharacterCompiler(tvm)
        tref = ccompiler.compileCharacters(root, 'utf_8', 0)
        ccompiler.writeCharactersToVM(tref)
        gref = ccompiler.compileCharacters(root, 'utf_8', 0)
        ccompiler.writeCharactersToVM(gref)
        # tree should be updated with same refs to vm
        for i in range(testLen):
            self.assertEqual(tref.childList[i].ref, gref.childList[i].ref, msg='Re-use of charactres - index {:d}'.format(i))

    def test_altTreeBuild(self):
        print("Alt tree building")
        pattern = '(a|b|c1|d12|ert|f|gh|hj|iyt|j7|k|l|mht|n8|o65|p|q2|r5|sr|ty|u|vg|ws|xx|y|z)((1a|1b|1c|1d|1e|1f|1g))*(a|b?|c|d|e|f|g|$|i)'
        test = (TYPE_GROUP, TYPE_GROUP, TYPE_ALT, TYPE_ALT,
                TYPE_ALT, TYPE_GROUP, TYPE_COMPILED, TYPE_GROUP, TYPE_COMPILED, TYPE_GROUP, TYPE_COMPILED, TYPE_COMPILED, TYPE_GROUP, TYPE_COMPILED, TYPE_COMPILED, TYPE_COMPILED,
                TYPE_ALT, TYPE_GROUP, TYPE_COMPILED, TYPE_COMPILED, TYPE_COMPILED, TYPE_GROUP, TYPE_COMPILED, TYPE_GROUP, TYPE_COMPILED, TYPE_COMPILED, TYPE_GROUP, TYPE_COMPILED, TYPE_COMPILED,
                TYPE_ALT, TYPE_GROUP, TYPE_COMPILED, TYPE_COMPILED, TYPE_COMPILED, TYPE_GROUP, TYPE_COMPILED, TYPE_COMPILED, TYPE_GROUP, TYPE_COMPILED, TYPE_GROUP, TYPE_COMPILED,
                TYPE_ALT, TYPE_GROUP, TYPE_COMPILED, TYPE_COMPILED, TYPE_COMPILED, TYPE_GROUP, TYPE_COMPILED, TYPE_COMPILED, TYPE_GROUP, TYPE_COMPILED, TYPE_COMPILED, TYPE_COMPILED, TYPE_GROUP, TYPE_COMPILED,
                TYPE_ALT, TYPE_ALT, TYPE_GROUP, TYPE_COMPILED, TYPE_COMPILED, TYPE_GROUP, TYPE_COMPILED, TYPE_COMPILED, TYPE_GROUP, TYPE_COMPILED, TYPE_COMPILED, TYPE_GROUP, TYPE_COMPILED, TYPE_COMPILED,
                TYPE_ALT, TYPE_GROUP, TYPE_COMPILED, TYPE_GROUP, TYPE_COMPILED, TYPE_COMPILED, TYPE_GROUP, TYPE_COMPILED, TYPE_COMPILED, TYPE_GROUP, TYPE_COMPILED, TYPE_COMPILED,
                TYPE_ALT, TYPE_GROUP, TYPE_COMPILED, TYPE_GROUP, TYPE_COMPILED,
                TYPE_REPEAT, TYPE_GROUP, TYPE_GROUP, TYPE_ALT,
                TYPE_ALT, TYPE_GROUP, TYPE_COMPILED, TYPE_COMPILED, TYPE_GROUP, TYPE_COMPILED, TYPE_COMPILED, TYPE_GROUP, TYPE_COMPILED, TYPE_COMPILED, TYPE_GROUP, TYPE_COMPILED, TYPE_COMPILED,
                TYPE_ALT, TYPE_GROUP, TYPE_COMPILED, TYPE_COMPILED, TYPE_GROUP, TYPE_COMPILED, TYPE_COMPILED, TYPE_GROUP, TYPE_COMPILED, TYPE_COMPILED,
                TYPE_GROUP, TYPE_ALT, TYPE_ALT, TYPE_GROUP, TYPE_PROG, TYPE_GROUP, TYPE_COMPILED, TYPE_GROUP, TYPE_REPEAT, TYPE_COMPILED, TYPE_GROUP, TYPE_COMPILED,
                TYPE_ALT, TYPE_GROUP, TYPE_COMPILED, TYPE_GROUP, TYPE_COMPILED, TYPE_GROUP, TYPE_COMPILED, TYPE_GROUP, TYPE_COMPILED, TYPE_ALT, TYPE_GROUP, TYPE_COMPILED)

        ptree = parseRE(pattern, 0)
        charCompiler = CharacterCompiler(Jsvm())
        ctree = charCompiler.compileCharacters(ptree, 'utf_8', 0)
        charCompiler.writeCharactersToVM(ctree)
        for i, (_, comp) in enumerate(ctree):
            self.assertEqual(comp.type, test[i], msg='alt tree building, test index {:d}'.format(i))


class TEST_ucd(unittest.TestCase):

    def test_compile(self):
        print('Unicode character compile: ascii')
        test = (('gc', 'letter'), ('', 'punctuation'), ('line-break', 'numeric'), ('numeric_TYPE', 'decimal'), ('script', 'common'), ('', 'latin'), ('', 'any'), ('', 'word'))
        compileEncoding('ascii')
        for p, v in test:
            np, nv = getPropertyValueNames(p, v)
            file   = getClassPath('ascii', np, nv)
            self.assertNotEqual(file, None, msg='ascii compile, failed pair=({},{})'.format(str(p), str(v)))
        # needs ascii to be pre installed
        self.assertTrue(isEncodingInstalled('ascii'), msg='is encding installed - ascii')
        self.assertFalse(isEncodingInstalled('klingon'), msg='is encding installed - fails')

    def test_propertyValues(self):
        print('Get Property Values')
        self.assertEqual(getPropertyValueNames(None, None), None, msg='Get property values - 1 - None input')
        self.assertEqual(getPropertyValueNames('eric', 'the viking'), None, msg='Get property values - 2 - not in scope')
        self.assertEqual(getPropertyValueNames('', ''), None, msg='Get property values - 2 - empty input')
        test = ('', 'alphabetic')
        self.assertEqual(getPropertyValueNames('', 'alpha'), test, msg='Get property values - 3 - alpha')
        self.assertEqual(getPropertyValueNames('alpha', ''), None, msg='Get property values - 4 - no value')
        test = ('general_category', 'cased_letter')
        self.assertEqual(getPropertyValueNames('gc', 'lc'), test, msg='Get property values - 5 - lc')
        test = ('script', 'greek')
        self.assertEqual(getPropertyValueNames('', 'greek'), test, msg='Get property values - 6 - greek')

    def test_normalise(self):
        print('Normalise Name')
        self.assertEqual(normaliseName(None), None, msg='Normalise name - 1 - None input')
        pattern = '  Normal-nAme tesT '
        test    =  'normal_name_test'
        self.assertEqual(normaliseName(pattern), test, msg='Normalise name - 2')

    def test_script_extensions(self):
        print('Script extensions')
        cc = CharClass('utf-8')
        props   = getPropertyValueNames('scx', 'arabic')
        fileRef  = getClassPath('utf-8', *props)
        cc.loadFromFile(fileRef)
        self.assertEqual(cc.getStateSize(), 33, msg='Script Extensions - 1 - extension size')
        cs = CharClass('utf-8')
        props   = getPropertyValueNames('script', 'arabic')
        fileRef  = getClassPath('utf-8', *props)
        cs.loadFromFile(fileRef)
        self.assertEqual(cs.getStateSize(), 32, msg='Script Extensions - 2 - script size')
        cc.difference(cs)
        self.assertEqual(cc.getStateSize(), 6, msg='Script Extensions - 3 - difference size')

    def test_matchindex(self):
        print('lastindex')
        buffer  = b'ab'
        patterns = (r'((ab))', r'(a)b', r'((a)(b))', r'(a)(b)')
        res      = (1, 1, 1, 2)
        for i, r in enumerate(res):
            match = jsre.search(patterns[i], buffer, encoding='ascii', flags=0)
            self.assertEqual(match.lastindex, r, msg='lastindex, pattern = {}'.format(patterns[i]))


class Test_regexLong(unittest.TestCase):
    #
    # primary regex tests
    #
    def test_regex(self):
        '''
        Test file format, values separated by ';' to allow csv lists in fields
        comment, sourceFile, referenceFile, encodingList, flags, altIndex, pattern
        '''
        __root = os.path.join(os.path.dirname(os.path.abspath(__file__)), TEST_ROOT)

        if not os.path.isdir(__root):
            raise SystemError("Test Directory not found in installation: {}".format(__root))

        print("Primary regex semantics ...")
        testCases = TestCases(os.path.join(__root, RE_TESTS), ';')
        for test in testCases:
            self.assertTrue(testFilePattern(__root, *test), msg='Regex distribution semantics: {}'.format(test[0]))

    def test_regex_dev(self):
        '''
        Test long running/large reference file cases, only used in development mode
        so warning only if files not avalable
        '''

        __root  = os.path.join(os.path.dirname(os.path.abspath(__file__)), DEV_TEST_ROOT)

        if not os.path.isdir(__root):
            testLog.warning("Testing running in distribution mode, development reference corpus not available")
        else:
            print("Regex Development (long running) tests")

            testCases = TestCases(os.path.join(__root, RE_TESTS), ';')
            for test in testCases:
                self.assertTrue(testFilePattern(__root, *test), msg='Regex development tests: {}'.format(test[0]))

    def test_ATT(self):
        __root  = os.path.join(os.path.dirname(os.path.abspath(__file__)), DEV_TEST_ROOT)

        if not os.path.isdir(__root):
            testLog.warning("Testing running in distribution mode, skipping AT&T regression")
        else:
            print("AT&T RE Regression Tests...")

            testCases = TestCases(os.path.join(__root, ATT_TESTS), '\t')
            for test in testCases:
                print("    " + test[1])
                ref = []
                if test[3] != 'NOMATCH':
                    for grp in re.findall(r'\(([?\d]+),([?\d]+)\)', test[3]):
                        if grp[0] == '?':
                            ref.append((-1, -1),)
                        else:
                            ref.append((int(grp[0]), int(grp[1])),)
                # delete trailing empty submatches
                for i in range(len(ref) - 1, -1, -1):
                    if ref[i][0] == -1:
                        del(ref[i])
                    else:
                        break

                testStringPattern(self, test[0], test[1], test[2], (ref,), None, True, "AT&T Regression")

    def test_match(self):
        print("jsre.match")
        pattern = r'start'
        buffer  = b'start and another start here'
        ref     = ((0, 5),)
        match   = jsre.match(pattern, buffer, encoding='ascii')
        self.assertEqual(match.span(0), ref[0], msg='module level match')

        print("jsre.purge")
        testkey = "encoding:ascii,flags:0,pattern:start"
        self.assertIn(testkey, _getModuleCache(), msg='cached module compiled regexes')
        jsre.purge()
        self.assertEqual(len(_getModuleCache()), 0, msg='cached module regex purge')

    def test_groups(self):
        print('Regex group modifiers')
        pattern = r'(??<.*>)(?#comment)(?P<name>[\p{alnum}]*)=(?P<value>[\p{alnum}]*)(?=(??<\\.*>))'
        target  = 'group test <start>res=good<\start> some other <not the same>value=pair<\> '
        test1    = [('<start>res=good', '<start>', 'res', 'good', '<\\start>'), ('<\start> some other <not the same>value=pair', '<\start> some other <not the same>', 'value', 'pair', '<\\>')]
        test2    = [('res', 'good'), ('value', 'pair')]
        res      = jsre.findall(pattern, target)
        self.assertEqual(res, test1, msg='group modifier test')
        hits = jsre.finditer(pattern, target)
        for i, match in enumerate(hits):
            self.assertEqual(match.group('name', 'value'), test2[i], msg='named group match recovery')

    def test_backreference(self):
        print('Backreferences')
        buffer  = ('abc123ab&bcd123b&def123&abc123abcdef123def',
                   'abc123abcdef123de',
                   'abc<z>de<z>pqr')
        pattern  = (r'([a-z]*)[0-9]+\1',
                    r'(?P<name>[a-z]*)[0-9]+(?P=name)',
                    r'.*(..*).*\1',
                    r'(.*).*\1',
                    r'(??.*(..*).*\2)')
        ref       = ((((3, 6), (3, 3)), ((12, 15), (12, 12)), ((20, 23), (20, 20)), ((24, 33), (24, 27)), ((33, 42), (33, 36))),
                     (((0, 9), (0, 3)), ((12, 15), (12, 12))),
                     (((0, 11), (3, 6)),),
                     (((0, 14), (0, 0)),),
                     (((0, 9), (0, 9), (3, 4)),))
        test      = ((0, 0, 0, None), (0, 1, 1, None), (1, 0, 0, None),
                     (1, 0, 0, 'ascii'), (1, 1, 1, 'ascii'),
                     (2, 2, 2, None), (3, 2, 3, None), (4, 2, 4, None))
        for i, tst in enumerate(test):
            testStringPattern(self, '', pattern[tst[0]], buffer[tst[1]], ref[tst[2]], tst[3], False, 'Backreferences {:d}'.format(i))

    def test_lazy(self):
        print('Lazy-greedy nesting')
        buffer  = b'brackets example {first{one},second{two}} end of example'
        pattern = r'(??\{([a-z,]+(\{.+\}))+\})'
        ref = (((17, 41), (17, 41), (18, 40), (23, 40)),)
        testStringPattern(self, '', pattern, buffer, ref, 'ascii', False, 'Lazy-greedy nesting')

        # now the opposite nesting
        pattern = r'\{([a-z,]+?(\{.+\}))+\}'
        ref = (((17, 41), (28, 40), (35, 40)),)
        testStringPattern(self, '', pattern, buffer, ref, 'ascii', False, 'Greedy-lazy nesting')

    def test_sector(self):
        print('Sector mode')
        pattern = r'(<\w*>)'
        test = [('<key1>', '<key1>'), ('<key6>', '<key6>'), ('<keyb>', '<keyb>'), ('<keyg>', '<keyg>'), ('<keyl>', '<keyl>'), ('<keyq>', '<keyq>')]
        offset = 7
        stride = 35
        __testRoot = os.path.join(os.path.dirname(os.path.abspath(__file__)), TEST_ROOT)
        if not os.path.isdir(__testRoot):
            raise SystemError("Test Database not found in installation".format(__testRoot))
        infile = open(os.path.join(__testRoot, 'images', 'test_sectorrmode'), 'rb')
        target = infile.read()
        regx = jsre.ReCompiler(pattern=pattern, encoding=('ascii',), flags=jsre.SECTOR, offset=offset, stride=stride).compile()
        res = regx.findall(target)
        self.assertEqual(test, res, msg='Sector Test')
        infile.close()

    def test_stringtarget(self):
        print('String target')
        pattern = r'<key\d>'
        target  = '<key0>quick browb<key1>jumpsover the lazy<key2> dog i forgot the fox<key3>'
        test1    = ((0, 6), (17, 23), (41, 47), (68, 74))
        for i, match in enumerate(jsre.finditer(pattern, target)):
            test = match.span()
            self.assertEqual(test, test1[i], msg='String target span, index {:d}'.format(i))

        target  = 'quick browbjumpsover the lazy<key2> dog i forgot the fox<key3>'
        test1   = (29, 35)
        match   = jsre.search(pattern, target)
        test = match.span()
        self.assertEqual(test, test1, msg='Search over string target')

    def test_altIndexing(self):
        print('Alt indexing')
        pattern = r'quick|time|arty'
        target  = 'now is the time for all good men to come to the aid of the quick brown fox united political party'
        test1   = ((11, 15), (59, 64), (93, 97))
        test2   = ('time', 'quick', 'arty')
        for i, match in enumerate(jsre.finditer(pattern, target, flags=jsre.INDEXALT)):
            test = match.span()
            key  = match.keypattern
            self.assertEqual(test, test1[i], msg='alt keywords - span index {:d}'.format(i))
            self.assertEqual(key, test2[i], msg='alt keywords - index text, index {:d}'.format(i))

        match = jsre.search(pattern, target, flags=jsre.INDEXALT)
        test = match.keypattern
        self.assertEqual(test, 'time', msg='altIndex from search')

    def test_matchResults(self):
        print('Match object results and groups')
        pattern = r'(?P<first>time)(.*|(?P<empty>nothingtosee))(?P<last>men)((zzz))?'
        target  = 'now is the time for all good men to come to the aid of the quick brown fox united political party'
        test1   = {'first': 'time', 'last': 'men', 'empty': 'default'}
        test2   = ('time for all good men', 'time', ' for all good ', 'NoMatch', 'men')
        match   = jsre.search(pattern, target)
        self.assertTrue(match, msg='match true check')
        testd   = match.groupdict('default')
        for vk in testd:
            self.assertEqual(test1[vk], testd[vk], msg='group dictionary')
        testd   = match.groups('NoMatch')
        self.assertEqual(test2, testd, msg='groups with default value')

        target  = target.encode()
        match = jsre.search(pattern, target)
        testd   = match.groups('NoMatch')
        self.assertEqual(test2, testd, msg='byte target groups with default value')

        test = match.group(5)
        self.assertEqual(test, None, msg='empty final group match')

        regex = jsre.ReCompiler(pattern='nothinogtoseeheremovealong', encoding='utf-8').compile()
        match   = regex.search(target)
        self.assertEqual(match, None, msg='None returned from empty search')

    def test_verboseRE(self):
        print('Verbose re')
        pattern = '''
                    ([0-9] { 1 , 3 } # first group
                    \.) { 3 }                 #   repeated
                       [0-9]
                       {1,3}   #'''
        target = 'the quick ip address of 192.168.0.29 jumps over the verbose re'
        match = jsre.search(pattern, target, flags=VERBOSE)
        self.assertTrue(match, msg='verbode re')

        pattern = 'aaa bbb#ccc'
        target  = '0123aaa bbb#ccc765'
        match = jsre.search(pattern, target)
        self.assertTrue(match, msg='space and hash in re not verbose')

    def test_multiplePatterns(self):
        print('Multiple res with overlapping patterns')
        pattern1 = r'<[a-z]{1,5}>'
        pattern2 = r'<\\[a-z]{1,5}>'
        target   = r'the quick brown <cow> jumps over the <\moon>'
        test     = [('<cow>',), ('<\\moon>',)]
        compiler = jsre.ReCompiler(encoding='cp1250')
        compiler.setPattern(pattern1)
        compiler.setPattern(pattern2)
        regex    = compiler.compile()
        res      = regex.findall(target.encode('cp1250'))
        self.assertEqual(res, test, msg='multiple res')

    def test_nestedOptionalRepeat(self):
        print('Nested optional repeat')
        pattern = r'([a-z]{,4}\.){,3}'
        buffer  = r'this is.a.test. .here.'
        ref = (((0, 0), (-1, -1)), ((1, 1), (-1, -1)), ((2, 2), (-1, -1)), ((3, 3), (-1, -1)), ((4, 4), (-1, -1)), ((5, 15), (10, 15)), ((15, 15), (-1, -1)), ((16, 22), (17, 22)))
        testStringPattern(self, '', pattern, buffer, ref, None, False, 'Nested optional repeat')

    def test_voidTreeComponents(self):
        print('Void tree components')
        pattern = r'az|([a-b&&0-1])*|([c-d&&0-1]|[e-f&&0-1])'
        test    = (TYPE_GROUP, TYPE_ALT, TYPE_GROUP, TYPE_COMPILED, TYPE_COMPILED)
        charCompiler = CharacterCompiler(Jsvm())
        ptree        = parseRE(pattern, 0)
        ctree        = charCompiler.compileCharacters(ptree, 'utf_8', 0)
        charCompiler.writeCharactersToVM(ctree)
        size = 0
        for i, (_, comp) in enumerate(ctree):
            self.assertEqual(comp.type, test[i], msg='Tree after removal of void components, index {:d}'.format(i))
            size += 1
        self.assertEqual(size, len(test), msg='Tree size after removal of void classes')

    def test_voidCharacter(self):
        print('Void characters')
        pattern = r'y[abc\u1090]*z'
        target  = '0123yabcz456'.encode('ascii')
        test1   = (TYPE_GROUP, TYPE_COMPILED, TYPE_REPEAT, TYPE_COMPILED, TYPE_COMPILED)
        test2   = 'yabcz'
        charCompiler = CharacterCompiler(Jsvm())
        ptree        = parseRE(pattern, 0)
        ctree        = charCompiler.compileCharacters(ptree, 'ascii', 0)
        charCompiler.writeCharactersToVM(ctree)
        size = 0
        for i, (_, comp) in enumerate(ctree):
            self.assertEqual(comp.type, test1[i], msg='Tree after removal of void components, index {:d}'.format(i))
            size += 1
        self.assertEqual(size, len(test1), msg='Tree after removal of void character')
        match = jsre.search(pattern, target, encoding='ascii')
        self.assertEqual(match.group(), test2, 'Re valid after removal of void character')

    def test_classNotInEncoding(self):
        print('Class in namespace not encoded')
        pattern = r'[\p{alpha}]|[\p{greek}]|a?'
        test    = (TYPE_GROUP, TYPE_ALT, TYPE_GROUP, TYPE_COMPILED, TYPE_GROUP, TYPE_REPEAT, TYPE_COMPILED)
        charCompiler = CharacterCompiler(Jsvm())
        ptree        = parseRE(pattern, 0)
        ctree        = charCompiler.compileCharacters(ptree, 'ascii', 0)
        charCompiler.writeCharactersToVM(ctree)
        size = 0
        for i, (_, comp) in enumerate(ctree):
            self.assertEqual(comp.type, test[i], msg='Tree after removal of void classes, index {:d}'.format(i))
            size += 1
        self.assertEqual(size, len(test), msg='Tree size after removal of void classes')

    def test_longRepeats(self):
        print('Long Repeats')
        pattern = r'a{70}zzb{,70}'
        buffer  = 'zaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaazzbb'
        ref     = (((3, 77),),)
        testStringPattern(self, '', pattern, buffer, ref, None, False, 'Long Repeats')

    def test_altGuardAndControl(self):
        print('Alt guard plus control')
        pattern = r'a{3}|b{3}'
        buffer  = 'zzaabbbzz'
        ref     = (((4, 7),),)
        testStringPattern(self, '', pattern, buffer, ref, None, False, 'Alt guard plus control 1')

        pattern = r'a(a*|[a-z]*)x'
        buffer = 'aabc01ababx12baaab0abx123abcfe0aaax'
        ref    = (((6, 11), (7, 10)), ((19, 22), (20, 21)), ((31, 35), (32, 34)))
        testStringPattern(self, '', pattern, buffer, ref, None, False, 'Alt guard plus control 2')

    def test_classRef(self):
        print('Class Referencing')
        pattern = r'((?:2[0-9]|[01]?[0-9])\.){3}'
        buffer  = 'abc1.2.3.4.5.6.7bdfefsja'
        ref     = (((3, 9), (7, 9)), ((9, 15), (13, 15)))
        testStringPattern(self, '', pattern, buffer, ref, None, False, 'Class Referencing')

    def test_nonCaptureRepeats(self):
        print('Non-capture repeated groups')
        pattern = r'(?:(?:2[0-9]|[01]?[0-9])\.){3}'
        buffer  = 'abc1.2.3.4.5.6.7bdfefsja'
        ref     = (((3, 9),), ((9, 15),),)
        testStringPattern(self, '', pattern, buffer, ref, None, False, 'Non-capture repeated groups')

    def test_graphemeClusterBreak(self):
        for encoding in ('utf_32_be', 'utf_8', 'utf_16_le'):
            print('Grapheme cluster break, encoding: {}'.format(encoding))
            testCases = UCDTestCases('grapheme_break_test')
            encodeFailCount = 0
            regex = jsre.ReCompiler(encoding=encoding, pattern='\X').compile()
            for target, test, info in testCases:
                matchCount = 0
                try:
                    buffer = target.encode(encoding)
                except:
                    encodeFailCount += 1
                    # print('unable to {} encode test: {}'.format(encoding, info))
                    continue
                testPos = convertPositions(target, test, encoding)
                for match in regex.finditer(buffer, 0, len(buffer), len(buffer) + 1):
                    self.assertIn(match.start(), testPos,
                                  msg="Grapheme Cluster break match, test = {}  byte position = {:d}".format(info, match.start()))
                    matchCount += 1
                self.assertEqual(matchCount, len(test),
                                 msg="Grapheme Cluster break count, test = {}, correct = {:d}, result = {:d}".format(info, len(test), matchCount))
            # Python does not encode the surrogates, so expect around 54 of the 400 or so tests to not encode
            self.assertLess(encodeFailCount, 55, msg="Grapheme Cluster Break, total failed encodings under {} = {:d}".format(encoding, encodeFailCount))


def unionTest(left, right):
    print('union test')
    ref = left.clone()
    ref.union(right)
    left.inverse()
    right.inverse()
    left.intersect(right)
    left.inverse()
    return ref.equals(left)


def intersectTest(left, right):
    print('intersect test')
    ref = left.clone()
    ref.intersect(right)
    left.inverse()
    right.inverse()
    left.union(right)
    left.inverse()
    return ref.equals(left)


def differenceTest(left, right):
    print('difference test')
    ref = left.clone()
    ref.difference(right)
    right.inverse()
    left.intersect(right)
    return ref.equals(left)


def getRawVM(trans, prog, start):
    #build a vm
    tvm = Jsvm()
    tvm.newStates(0, len(trans))
    for i in range(len(trans)):
        tvm.newTransition(i, trans[i], VM_CHARACTER_OK)

    #Build program
    pmap = {}
    pmap[0] = 0
    for i in range(len(prog)):
        code = []
        #program linking
        for j in range(len(prog[i])):
            if prog[i][j][0] == VM_INSTR_NEW_THREAD:
                code.append((prog[i][j][0], prog[i][j][1], pmap[prog[i][j][2]], prog[i][j][3]))
            else:
                code.append(prog[i][j])

        pmap[i] = tvm.newProgram(code)

    #Build starts
    for i in range(len(start)):  # here just command and mapped prog address
        tvm.newStart(i, (start[i][0], pmap[start[i][1]], 2, 0, 0, 0, 0, [0xFFFFFFFF] * 32))

    return tvm


def _testGraphEquals(tree, graph):
    ''' checks that the graph is the same byte encoding as the tree
        (will also check that two trees or two graphs are equivalent)
    '''
    visited = {}
    if not _testPublishNode(tree, graph, 0, 0, visited):
        return False
    if len(visited) != len(graph.leafs):
        return False
    return True


def _testPublishNode(tree, graph, tk, gk, visited):
    # check leafs if present
    if (tk in tree.leafs) and (gk not in graph.leafs):
        return False
    if (tk not in tree.leafs) and (gk in graph.leafs):
        return False
    if (tk in tree.leafs):
        if _equalRanges(tree.leafs[tk], graph.leafs[gk]):
            visited[gk] = True
        else:
            return False

    # check outward transition
    if (tk not in tree.transitions) and (gk in graph.transitions):
        return False
    if (tk in tree.transitions) and (gk not in graph.transitions):
        return False
    if tk not in tree.transitions:
        return True

    # recurse over children
    for vk in tree.transitions[tk]:
        if vk not in graph.transitions[gk]:
            return False
        ntk = tree.transitions[tk][vk]
        ngk = graph.transitions[gk][vk]
        if not _testPublishNode(tree, graph, ntk, ngk, visited):
            return False
    return True


def testStringPattern(testcase, control, pattern, target, ref, encoding, first, message):
    ''' simple search test of a pattern against the matches and sub-matches that result
        supports AT&T style regression. Assumes string inputs.

        if target is a string then if encoding not specified it is encoded with utf-32-be
        and the position correction set to true to index characters

        ref is ( ((span hit 0), (span group 0.1)...), ((span hit 1), (span group 1.1)...), ... )

        if first then only the first match (search) will be checked (ie AT&T)
    '''
    kargs = {}
    flags = 0
    if 'i' in control:
        flags += IGNORECASE
    kargs['flags'] = flags

    if '$' in control:
            # no good choices here, assumes byte characters only
            pattern = pattern.encode('latin-1').decode('unicode_escape')
            target  = target.encode('latin-1').decode('unicode_escape')
    if target == 'NULL':
        target = ''

    if len(ref[0]) == 0:
        ref = ()

    if encoding:
        kargs['encoding'] = encoding

    if isinstance(target, str):
        if not encoding:
            kargs['encoding']               = 'utf_32_be'
            kargs['encodingSizeCorrection'] = 4
        if isinstance(kargs['encoding'], str):
            target = target.encode(encoding=kargs['encoding'])
        else:
            target = target.encode(encoding=kargs['encoding'][0])

    regex = jsre.ReCompiler(pattern=pattern, **kargs).compile()

    count = 0
    for m, match in enumerate(regex.finditer(target)):
        count += 1
        for i in range(len(ref[m])):
            testcase.assertEqual(match.span(i), ref[m][i], msg="{} re = {} bad match {:d}.{}, should be {}".format(message, pattern, m, str(match.span(i)), str(ref[m][i])))
        if first:
            break
    testcase.assertEqual(count, len(ref), msg="{} incorrect number of matches: {:d} should be {:d}".format(message, count, len(ref)))


def testFilePattern(root, comment, sourceFile, referenceFile, encoding, flags, altIndex, pattern):
    ''' run pattern againt sourceFile and check result against reference.
    '''
    print('  ' + comment)
    testPath = os.path.join(root, TEST_IMAGES, sourceFile)

    try:
        testPath = os.path.join(root, TEST_IMAGES, sourceFile)
        inFile = BinaryInput(testPath)
    except:
        print("unable to open source file: " + sourceFile)
        return False
    try:
        refFile = open(os.path.join(root, TEST_REFERENCE, referenceFile), 'r')
    except:
        print("unable to open reference file: " + referenceFile)
        return False
    regx = jsre.ReCompiler(pattern=pattern, encoding=encoding.split(','), flags=int(flags)).compile()
    recordIndex = 0
    hitsChecked = 0
    for buffer, size in inFile:
        hits = []
        #need to use the legal part of the record, not any value extension
        for match in regx.finditer(buffer, 0, size):
            if int(altIndex) == 0:
                hits.append((match.encoding, match.start(), getPrintString(match, buffer)))
            else:
                hits.append((match.encoding, match.start(), match.keypattern, getPrintString(match, buffer)))
        hits.sort()
        # check sizes
        if len(hits) > 0:
            hitsChecked += 1
            refLine = refFile.readline().rstrip('\n').split(',')
            if int(refLine[0]) != recordIndex or int(refLine[1]) != len(hits):
                print("Record offset {}: incorrect offset or number of hits".format(refLine[0]))
                return False
            for hit in hits:
                # check hit metadata
                splitby = 2 if (int(altIndex) == 0) else 3
                refLine = refFile.readline().rstrip('\n').split(',', splitby)
                if (hit[0] != refLine[0]) or (hit[1] != int(refLine[1])) or ((int(altIndex) != 0) and (hit[2] != refLine[2])):
                    print("Record offset {}, hit at {}, incorrect result metadata:".format(recordIndex, refLine[1]))
                    return False
                if hit[splitby] != refLine[splitby]:
                    print("Record offset {}, hit should be: \n{}\nincorrect result: \n{}".format(recordIndex, refLine[splitby], hit[splitby]))
                    return False

        recordIndex += TEST_BUFFER_SIZE
    inFile.close()
    if hitsChecked == 0:
        print("No hits returned to check")
        return False
    refFile.close()
    return True


def testPrefix(pattern, prefix):
    ''' tests that a pattern generated a given prefix'''

    # make scan prefix
    ptree = parseRE(pattern, 0)
    compiler = CharacterCompiler(None)
    ctree = compiler.compileCharacters(ptree, 'utf_8', 0)

    #fake publish to VM
    charIndex = -1
    for comp in ctree.filteredBy(TYPE_CHARCLASS):
        if comp.pattern in compiler.registry:
            charIndex = compiler.registry['utf_8'][comp.pattern]
        else:
            charIndex += 1
            compiler.registry['utf_8'][comp.pattern] = charIndex
            compiler.registry['utf_8'][charIndex]    = comp.tmpCharClass
        del(comp.tmpCharClass)
        comp.update(TYPE_COMPILED, charIndex)

    # point any referenced character classes to the correct compiled object
    for _, comp in ctree:
        if hasattr(comp, 'childList'):
            for i, child in enumerate(comp.childList):
                if child.type == TYPE_CLASSREF:
                    comp.childList[i] = compiler.classRefRegistry[child.pattern]

    scanList = compiler._getPreview(ctree, 6)

    # test
    if prefix == None and scanList == None:
        return True
    if len(prefix) != len(scanList):
        return False
    for i, sourceList in enumerate(prefix):
        ref = CharClass('utf_8')
        for ch in sourceList:
            cc = CharClass('utf_8')
            cc.loadFromCharacter(ch)
            ref.union(cc)
        if not ref.equals(scanList[i]):
            return False
    return True


def convertPositions(target, positions, encoding):
    ''' converts positions in a string to positions in a byte string
    by enumerating lengths. For testing only!
    '''
    newpos = []
    for pos in positions:
        try:
            newpos.append(len(target[:pos].encode(encoding)))
        except:
            return None
    return newpos


def getPrintString(match, buffer):
    ''' returns the match string if ascii printable, otherwise bytes in hex
    '''
    res = match.group()
    if jsre.search(RE_NOTASCIIPRINT, res):
        res = 'hex: ' + ''.join(["%02X " % x for x in buffer[match.start():match.end()]]).strip()
    return res


class TestCases():
    '''    reads test cases from file, ignores blank and comment lines
           returns separated list via iterator
    '''

    def __init__(self, path, separator=','):
        if not os.path.isfile(path):
            raise SystemError("Test file not found in installation: {}".format(path))
        self.tests = open(path, 'r')
        self.separator = separator

    def __iter__(self):
        return self

    def __next__(self):
        while True:
            # get next test
            testLine = self.tests.readline()
            if testLine == '':
                self.tests.close()
                raise StopIteration
            # avoid blank or comment lines
            testLine = testLine.rstrip('\n')
            if testLine == '' or testLine[0] == '#':
                continue
            test = [f for f in testLine.split(self.separator) if f]
            return test


class BinaryInput():
    '''    very sawn-off version of jigsaw utility BI to allow
           reobjects testing to stand-alone
    '''

    def __init__(self, path):
        self.path        = path
        self.blocksize   = TEST_BUFFER_SIZE
        try:
            # do the buffering here not in the system
            self.file        = open(self.path, 'rb', buffering=0)
        except:
            #if here really a bug, this should already have been checked
            raise SystemError("Failed to open input file or device: " + self.path)
        self.currBlock = None
        self.start     = 0

    def __iter__(self):
        ''' iteration initiator
        '''
        return self

    def __next__(self):
        """ provide the next block """
        if self.currBlock == None:
            #fetch first block
            self.currBlock = self.file.read(self.blocksize * 2)
        else:
            #normal next block
            self.currBlock = self.currBlock[self.blocksize:] + self.file.read(self.blocksize)
            self.start = self.start + self.blocksize
        if len(self.currBlock) == 0:
            self.close()
            raise StopIteration
        size = self.blocksize if self.blocksize < len(self.currBlock) else len(self.currBlock)
        return self.currBlock, size

    def close(self):
        self.file.close()


def runTest():
    unittest.main()

if __name__ == "__main__":
    runTest()
