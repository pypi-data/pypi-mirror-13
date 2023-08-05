'''
Provides character classes, including file storage and recovery and set operations.

@author: Howard Chivers

Copyright (c) 2015, Howard Chivers
All rights reserved.

'''
import logging
import os
import struct
from collections import namedtuple
from zlib import crc32

#character transition leaf marker (used in place of destination state for transition)
VM_CHARACTER_OK            = 0xFFFF    # character transition success

COMPILE_ROOT         = 'JSRE_Compiled'

charClassLog         = logging.getLogger("CharClass")
__compilePath        = os.path.join(os.path.dirname(os.path.abspath(__file__)), COMPILE_ROOT)

# ranges here are inclusive
Range                = namedtuple('Range', ('first', 'last'))

FILE_FORMAT_MAGIC    = 0x7EB0 + 2
FILE_STATESIZE_LIMIT = 65521
BYTE_HASH_FIELDSIZE  = 65521
RANGE_HASH_FIELDSIZE = 4294967291

__allCharacters      = {}   # dict of encoding->\p{any}


class CharClass(object):
    '''CharClass represents a character class as a byte-compiled tree

    The normal form for a character class is a (deterministic) tree. In
    this form the various logic operations are sound. The tree can be
    collapsed into a more compact state representation for publication
    to the vm.

    Primary functions:
        Load from character, range or file
        Store to file or vm
        union, intersection, difference, inverse, equality, clone

    ISSUES:
    Does not process surrogates - from Python 3.4 surrogates are not processed
    in the utf codecs.  See https://docs.python.org/3/library/codecs.html

    The behaviour of set operations is undefined for non-deterministic
    character encodings, although Union will allow them to be loaded
    and therefore identified.
    '''
    __loadRegistry       = {}   # dict to cache loaded classes

    def __init__(self, encoding, ifirstChar=None, ilastChar=None):
        ''' build class, optionally from a single character or a range

        Params:
            ifirstChar, ilastChar    inclusive range,
                                     integers representing unicode code points
            encoding                 string with valid python codec name
        '''
        self.encoding       = encoding
        self._newState()
        if ifirstChar != None:
            self.loadFromRange(ifirstChar, ilastChar)

    def _newState(self):
        ''' reset/initialise character class
        '''
        self.transitions    = {}   # state -> {value->nextState}
        self.leafs          = {}   # state -> [leaf range]
        self.stateSize      = 0    # number of states used

    def loadFromRange(self, ifirstChar, ilastChar):
        '''load character class from a range of integer code points

        Params:
            ifirstChar,ilastChar    the range is inclusive,
                                    characters are integer code points
        '''
        self._newState()
        if ilastChar == None or ifirstChar == ilastChar:
            self.loadFromCharacter(chr(ifirstChar))
        else:
            temp = CharClass(self.encoding)
            for i in range(ifirstChar, ilastChar + 1):
                temp.union(CharClass(self.encoding, ifirstChar=i))
                if i & 0x7F == 0:
                    #every 128 characters dump state
                    self.union(temp)
                    temp._newState()
            #add in final state
            self.union(temp)

    def loadByteRange(self, ifirstByte, ilastByte):
        ''' load a byte range (e.g. from hex range) in ascii.

        This will load a byte range regardless of the class encoding.

        Params:
            iFirstByte,ilastByte    range is inclusive
                                    bytes are integers
        '''
        if (ifirstByte > 255) or (ilastByte > 255):
            raise ValueError("Invalid Byte Range ({:d} - {:d}".format(ifirstByte, ilastByte))

        newRange = Range(ifirstByte, ilastByte) if ifirstByte < ilastByte else Range(ilastByte, ifirstByte)
        if 0 in self.leafs:
            self.leafs[0].append(newRange)
            _normaliseRanges(self.leafs[0])
        else:
            self.leafs[0]  = [newRange]
            self.stateSize = 1

    def loadFromCharacter(self, cString):
        '''Initialise object all characters from a string

        Note that the string is encoded as a single character.

        Normal behaviour is for characters that cannot be encoded to silently
        return an empty code set. This is (probably) OK for large character
        sets but caller should check that single characters in an RE have been
        encoded by using isEmpty().
        '''
        self._newState()
        try:
            bchar = cString.encode(self.encoding)
        except:
            # return empty character
            return

        self.transitions = {}
        self.leafs       = {}
        self.stateSize   = len(bchar)
        last             = len(bchar) - 1

        for i in range(last):
            self.transitions[i] = {bchar[i]: i + 1}

        self.leafs[last] = [Range(bchar[last], bchar[last])]

    def isEmpty(self):
        ''' Returns true if the character class is empty (null)
        '''
        if self.stateSize == 0:
            return True
        return False

    def getStateSize(self):
        ''' Returns state size of character class
        '''
        return self.stateSize

    def _selfLoad(self, tcc):
        ''' Load the state into self
        '''
        self.transitions = tcc.transitions
        self.leafs       = tcc.leafs
        self.stateSize   = tcc.stateSize
        self.encoding    = tcc.encoding

    def toFile(self, fileName):
        ''' Write character class to named file.

        File format:  (int16 unless noted)
          header:            formatVersion,encoding,stateSize,
                             transitionCount,leafCount
          transitions:       [state, numberoftransitions [nextState,value{byte}]]
          leafs:             [state,number of ranges  [first[byte],last[byte]]
                             checksum
        '''
        # protect from very large character classes
        if self.stateSize > FILE_STATESIZE_LIMIT:
            charClassLog.warning("State limit exceeded in character class, not written to file, state size = {}, file = {}".format(self.stateSize, fileName))
            return

        # protect from non-deterministic classes
        ndStateCount = len(self._mapNondeterministicStates())
        if ndStateCount > 0:
            charClassLog.warning("Character is internally non-deterministic (" + fileName + "), will not be written")
            return

        try:
            #check file
            if os.path.isfile(fileName):
                charClassLog.warning("Character output file already exists (" + fileName + "), will be overwritten")

            #open new file
            if not os.path.exists(os.path.dirname(fileName)):
                os.makedirs(os.path.dirname(fileName))
            outFile = open(fileName, 'wb')
        except Exception as e:
            charClassLog.error("OS IO error when trying to open character class file ({}) for writing, error: {}".format(fileName, str(e)))
            exit(1)

        encoding = self.encoding.encode('utf-8')
        try:
            bout = bytearray(struct.pack('=HHHHH', FILE_FORMAT_MAGIC,
                                         len(encoding), self.stateSize,
                                         len(self.transitions), len(self.leafs)))
            bout.extend(encoding)

            for tk in self.transitions:
                bout.extend(struct.pack('=HH', tk, len(self.transitions[tk])))
                for valueKey in self.transitions[tk]:
                    bout.extend(struct.pack('=BH', valueKey,
                                            self.transitions[tk][valueKey]))

            for tk in self.leafs:
                bout.extend(struct.pack('=HH', tk, len(self.leafs[tk])))
                for tr in self.leafs[tk]:
                    bout.extend(struct.pack('=BB', tr.first, tr.last))
            bhash = crc32(bytes(bout)) % BYTE_HASH_FIELDSIZE
            #print('out  ' + str(bytes(bout)) + '   ' + str(bhash))
            bout.extend(struct.pack('=H', bhash))
            outFile.write(bytes(bout))
            outFile.close()

        except Exception as e:
            charClassLog.error("Error when trying to write character class file ({}) for writing, error: {}".format(self.fileName, str(e)))
            exit(1)

    def loadFromFile(self, fileName):
        ''' Rebuild state of self from the named character class file.

        See toFile() for file format.
        '''
        #check file
        if not os.path.isfile(fileName):
            raise FileNotFoundError("Character file (" + fileName + ") not found")

        if fileName in CharClass.__loadRegistry:
            self._selfLoad(CharClass.__loadRegistry[fileName].clone())
            return

        try:
            inFile = open(fileName, 'rb')
            inData = inFile.read()
            inFile.close()
        except Exception as e:
            charClassLog.error("OS IO error when trying to open character class file ({}), error: {}".format(fileName, str(e)))
            exit(1)

        try:
            #checksum test
            check = crc32(bytes(inData[:-2])) % BYTE_HASH_FIELDSIZE
            test = struct.unpack('=H', inData[-2:])[0]
            if test != check:
                charClassLog.error("Checksum error when reading from character class file ({})".format(fileName))
                exit(1)

            version, encodeLen, self.stateSize, transLen, leafLen = struct.unpack_from('=HHHHH', inData, 0)
            if version != FILE_FORMAT_MAGIC:
                charClassLog.error("Format Version error when reading from character class file ({})".format(fileName))
                exit(1)
            start = struct.calcsize('=HHHHH')

            self.encoding = inData[start:start + encodeLen].decode('utf-8')
            start += encodeLen

            self.transitions = {}
            for _i in range(transLen):
                state, count = struct.unpack_from('=HH', inData, start)
                start += struct.calcsize('=HH')
                res = {}
                for _j in range(count):
                    v, s = struct.unpack_from('=BH', inData, start)
                    res[v] = s
                    start += struct.calcsize('=BH')
                self.transitions[state] = res

            self.leafs = {}
            for _i in range(leafLen):
                state, count = struct.unpack_from('=HH', inData, start)
                start += struct.calcsize('=HH')
                res = []
                for _j in range(count):
                    res.append(Range._make(struct.unpack_from('=BB',
                                                              inData, start)))
                    start += struct.calcsize('=BB')
                self.leafs[state] = res

            # cache the character
            CharClass.__loadRegistry[fileName] = self.clone()

        except Exception as e:
            charClassLog.error("Conversion error when trying to decode character class file ({}), error: {}".format(fileName, str(e)))
            exit(1)

    def writeGDF(self, fileName):
        ''' Write character class to .gdf graph file.

        warning - not all info is preserved
        artificial nodes corresponding to leafs are generated and
        given numbers 1000+ the source node
        transitions are labelled with the action value
        '''
        path = fileName + '.gdf'

        #check directory?
        try:
            if not os.path.exists(os.path.dirname(path)):
                os.makedirs(os.path.dirname(fileName))
            gdfFile = open(path, 'w')
        except Exception as e:
            charClassLog.error("OS IO error when trying to open gdf file ({}) for writing, error: {}".format(fileName, str(e)))
            exit(1)

        gdfFile.write('nodedef> name VARCHAR,label VARCHAR,Modularity Class VARCHAR\n')
        for p in range(self.stateSize):
            mode = 1
            gdfFile.write('"{0}","{0}","{1:d}"\n'.format(p, mode))
        for p in self.leafs:
            mode = 2
            for i in range(len(self.leafs[p])):
                gdfFile.write('"{0:d}R{1:d}","{0:d}R{1:d}","{1:d}"\n'.format(p, i, mode))

        gdfFile.write('edgedef> node1,node2,label VARCHAR,directed BOOLEAN\n')
        for s in self.transitions:
            src = self.transitions[s]
            for vk in src:
                gdfFile.write('"{:d}","{:d}","{:X}",true\n'.format(s, src[vk], vk))
        for s in self.leafs:
            src = self.leafs[s]
            for i in range(len(src)):
                gdfFile.write('"{0:d}","{0:d}R{1:d}","{2:X}-{3:X}",true\n'.format(s, i, src[i].first, src[i].last))

        gdfFile.close()

    #**************************************************************************
    #      Public Set Operations: union, difference, intersection,
    #                             equality, negate, clone
    #**************************************************************************

    def union(self, right):
        ''' Self is updated with the union with right

        right is unmodified
        '''
        _checkEncoding(self, right)
        #identity and zero checks
        if right is self:
            return self
        if self.stateSize == 0:
            self._selfLoad(right.clone())
            return self
        if right.stateSize == 0:
            return self

        oldStateSize = self.stateSize

        # maps from states in right to states in res
        # and increase states in res if necessary
        self.stateSize, cmap = _mapStates(self, right)

        #merge right into self
        for rs in right.transitions:
            tdict = right.transitions[rs]
            if cmap[rs] < oldStateSize:
                # state is identical to existing state,
                # need to copy in any new transitions
                for vk in tdict:
                    if cmap[tdict[vk]] >= oldStateSize:

                        # transition points to a merged state,
                        # so transition be rewritten and added
                        if cmap[rs] not in self.transitions:
                            self.transitions[cmap[rs]] = {}
                        self.transitions[cmap[rs]][vk] = cmap[tdict[vk]]
            else:
                # new state to be added
                self.transitions[cmap[rs]] = {}
                for vk in tdict:
                    self.transitions[cmap[rs]][vk] = cmap[tdict[vk]]

        #merge leaf nodes
        for rl in right.leafs:
            if cmap[rl] in self.leafs:
                #existing leaf nodes must be merged
                for r in right.leafs[rl]:
                    self.leafs[cmap[rl]].append(r)
                self.leafs[cmap[rl]] = _normaliseRanges(self.leafs[cmap[rl]])
            else:
                #can just copy new leaf node to state
                self.leafs[cmap[rl]] = list(right.leafs[rl])

        return self

    def intersect(self, right):
        ''' Intersect self with right
        '''
        _checkEncoding(self, right)

        if self.stateSize == 0 or right.stateSize == 0:
            self._selfLoad(CharClass(self.encoding))
            return self
        if right is self:
            return self

        #maps from states in right to states in self
        cmap = _mapStates(self, right)[1]

        # intersect any mapped leaf ranges
        # this should be all that is necessary
        # assumes that transition model is consistent
        tleafs = {}
        for rk in right.leafs:
            if cmap[rk] in self.leafs:
                newRange = _intersectRanges(self.leafs[cmap[rk]], right.leafs[rk])
                if len(newRange) > 0:
                    tleafs[cmap[rk]] = newRange
        self.leafs = tleafs

        # throw away any states that don't terminate in a leaf
        # or result in full leaf range
        self._trimNonTerminatingStates()
        self._compactStates()
        return self

    def difference(self, right):
        ''' Remove elements from self that are present in right.
        '''
        _checkEncoding(self, right)

        if right.stateSize == 0 or self.stateSize == 0:
            return self
        if right is self:
            self._selfLoad(CharClass(self.encoding))
            return self

        # maps from states in right to states in self
        cmap = _mapStates(self, right)[1]

        # first difference any mapped ranges
        for rk in right.leafs:
            if cmap[rk] in self.leafs:
                self.leafs[cmap[rk]] = _differenceRanges(self.leafs[cmap[rk]],
                                                         right.leafs[rk])
                if self.leafs[cmap[rk]] == []:
                    del self.leafs[cmap[rk]]

        # remove states if possible
        self._trimNonTerminatingStates()
        self._compactStates()
        return self

    def inverse(self):
        '''
        This returns the inverse of a character class by set difference between
        'any' and that class.

        Note that this preserves multi-byte encoding, not just byte logic.
        '''
        cc = getAny(self.encoding)
        cc.difference(self)
        self._selfLoad(cc)
        return self

    def equals(self, test):
        ''' Test if a character class is equal to self.

        This is a deep test that maps the two classes and
        checks if they produce the same result. Returns true if equal.
        '''
        # the basics!
        if test is self:
            return True
        if test.stateSize != self.stateSize:
            return False
        if test.encoding != self.encoding:
            return False
        if len(self.leafs) != len(test.leafs):
            return False
        if len(self.transitions) != len(test.transitions):
            return False

        # map states together
        sizeCheck, cmap = _mapStates(self, test)

        if sizeCheck != self.stateSize:
            return False

        # check leaf nodes
        for tk in test.leafs:
            if cmap[tk] not in self.leafs:
                # cannot match leaf
                return False
            if not _equalRanges(self.leafs[cmap[tk]], test.leafs[tk]):
                return False

        return True

    def clone(self):
        ''' Return a clone of this character class.

        This is deep enough to separate child objects.
        '''
        res = CharClass(self.encoding)
        for sk in self.transitions:
            res.transitions[sk] = self.transitions[sk].copy()
        for sk in self.leafs:
            res.leafs[sk] = list(self.leafs[sk])
        res.stateSize = self.stateSize
        return res

    def addAsSequence(self, right):
        ''' Adds the given character class as a sequence from
            self. Can be used with tree or graph types

            This renumbers right above self then modifies
            leafs in self to transitions to the root of the new states
        '''

        if right == None or right.isEmpty():
            return self
        _checkEncoding(self, right)

        newcc = right.clone() if self is right else right

        base = self.stateSize
        #rewrite leafs to point at extra character base
        for sk in self.leafs:
            if sk not in self.transitions:
                self.transitions[sk] = {}
            for valRange in self.leafs[sk]:
                for val in range(valRange.first, valRange.last + 1):
                    self.transitions[sk][val] = base
        del(self.leafs)
        self.leafs = {}

        #copy extra leafs and transitions
        for sk in newcc.leafs:
            self.leafs[base + sk] = list(newcc.leafs[sk])
        for sk in newcc.transitions:
            self.transitions[base + sk] = {}
            for val in newcc.transitions[sk]:
                self.transitions[base + sk][val] = base + newcc.transitions[sk][val]
        self.stateSize += newcc.stateSize

        return self

    def publishToGraph(self):
        ''' Compress character class tree into compact graph.

        Compiled form character classes are trees, this method compresses the
        tree into a graph for actual use by working from the leaves toward the
        root and joining matching cases. NOTE after this has been used the
        behaviour of set operations is completely unspecified, this is a
        finalisation process before the character class is exported to the VM
        '''

        # build a map of distances of states from root
        # and an inverse state transition table
        stateDepth = self._mapStateDistance()
        depends    = self._inverseStateDirectory()

        # hash all rangeLength
        # candidate matches are listed as hash -> state
        candidates = {}

        # fill list with entries for terminating rangeLlists
        for s in self.leafs:
            if s not in self.transitions:
                # terminating rangelist
                rhash = _hashRangeList(self.leafs[s], stateDepth[s])
                if rhash not in candidates:
                    candidates[rhash] = []
                candidates[rhash].append(s)

        # for each identical range, join states recursively
        for hk in candidates:
            joinList = candidates[hk]
            left     = joinList[0]
            for s in range(1, len(joinList)):
                # _joinStates(self, depends, joinList[0], joinList[s])
                # can leave out many of the checks if first loop is in line
                # relies on good hash
                right = joinList[s]

                # protects against hash collisions
                if not _equalRanges(self.leafs[left], self.leafs[right]):
                    return
                del self.leafs[right]

                # adjust transition to point at new state
                sourceLeft  = depends[left][0]
                sourceRight = depends[right][0]

                # redirect old transition, then return if path to here is common
                self.transitions[sourceRight][depends[right][1]] = left
                if sourceLeft == sourceRight:
                    continue

                # check if source states might be merged.

                #do they have the same transitions
                if self.transitions[sourceLeft] != self.transitions[sourceRight]:
                    continue

                #check leafs on call down
                self._joinStates(depends, sourceLeft, sourceRight)

        #compact state indexes
        self._compactStates()
        return

    def publishToVM(self, vm):
        ''' Publish the character class to a VM

        Failure raises exception up to caller except an allocation error which
        returns None.

        If successful the vm base index of the state is returned
        setting compact=False prevents compression of tree to graph
        prior to writing to the vm (either write the tree or a
        previously published graph)

        If an empty class is written then a single sate is allocated,
        which will be empty.

        Most of the failures that this might raise are compile errors
        reported by the vm. They all indicate system errors in the
        python compiling the re!
        '''
        baseState = vm.nextState()
        toAllocate = 1 if self.isEmpty() else self.stateSize

        #make space
        try:
            vm.newStates(baseState, baseState + toAllocate)
        except Exception as e:
            charClassLog.error("Error while allocating VM states: " + str(e))
            return None

        #write transitions
        for sk in self.transitions:
            tdict = self.transitions[sk]
            for tk in tdict:
                vm.newTransitionRange(baseState + sk, tk, tk, baseState + tdict[tk])

        for sk in self.leafs:
            rlist = self.leafs[sk]
            for r in rlist:
                vm.newTransitionRange(baseState + sk, r.first, r.last, VM_CHARACTER_OK)
        return baseState

    def _joinStates(self, depends, left, right):
        ''' Join state right to state left and follow recursively towards root.

        This is used in turning a tree into a more compact graph. Comparable
        leaf nodes are joined then the process works recursively toward tree root
        attempting to eliminate more states.

        The entry to this must ensure that left and right are terminating leafs -
        ie that the states do not have transitions

        Params:
            left,right    states to join
            depends       an inverse map states->parents
        '''
        #only one leaf present without the other
        if not left in self.leafs and right in self.leafs:
            return
        if left in self.leafs and not right in self.leafs:
            return

        if left in self.leafs and right in self.leafs:
            if not _equalRanges(self.leafs[left], self.leafs[right]):
                return
            # abandon leaf to right
            del self.leafs[right]

        # adjust transition to point at new state
        sourceLeft  = depends[left][0]
        sourceRight = depends[right][0]

        # redirect old transition, then return if path to here is common
        self.transitions[sourceRight][depends[right][1]] = left
        if right in self.transitions:
            del self.transitions[right]
        if sourceLeft == sourceRight:
            return

        # check if source states can be merged.

        #do they have the same transitions
        if self.transitions[sourceLeft] != self.transitions[sourceRight]:
            return

        #leafs will be checked on call down
        self._joinStates(depends, sourceLeft, sourceRight)

    def _mapNondeterministicStates(self):
        ''' Return a dictionary any non-deterministic states in the given tree.

        This finds non-deterministic states in a compiled character tree.

        The only possibility for non-determinism is a state which has a
        transition and a leaf for the same value.

        Returns:
            a state-indexed directory the entries of which are a list of
            non-deterministic values.
        '''
        ndStates = {}
        for sk in self.transitions:
            if sk in self.leafs:
                #state has both leaf and transitions
                ndvs  = _intersectRangesWithValues(self.leafs[sk], [v for v in self.transitions[sk]])
                if ndvs != []:
                    ndStates[sk] = ndvs
        return ndStates

    def _mapStateDistance(self):
        '''Return a dictionary which maps states to distance from root.

        Returns:
            a tuple of (map,maxDepthFound)
        '''
        res = {0: 0}
        toDo = [k for k in self.transitions]
        while toDo:
            nextWork = []
            for sk in toDo:
                trans = self.transitions[sk]
                if sk in res:
                    # have start so can map root distance
                    for vk in trans:
                        res[trans[vk]] = res[sk] + 1
                else:
                    # start not yet in result, do next time
                    nextWork.append(sk)
            toDo = nextWork
        return res

    def _inverseStateDirectory(self):
        ''' Return a dictionary which maps states to their parents.

        This builds a dictionary which shows the parent of any state. (Recall this
        is still a tree, so unique).

        Returns:
            destinationState -> (sourceState,transitionValue)
        '''
        imap = {}
        for s in self.transitions:
            src = self.transitions[s]
            for vk in src:
                imap[src[vk]] = (s, vk)
        return imap

    # @coverage
    def _compactStates(self):
        ''' Compress a character class to minimum state size.

        This takes a charClass in which some states and transitions have been
        removed and renumbers it to the minimum state size.
        '''

        if self.isEmpty():
            return

        # find current top
        for top in range(self.stateSize - 1, -1, -1):
            if top in self.transitions or top in self.leafs:
                break

        # restore to normal range
        top += 1

        # find spare slots
        spareStates = []
        for i in range(top):
            if i not in self.transitions and i not in self.leafs:
                spareStates.append(i)
        if len(spareStates) == 0:
            # already compressed - any missing are at the top of the range
            self.stateSize = top
            return

        # map top states into spare slots
        rmap = {}

        slot = 0
        state = top - 1
        while slot < len(spareStates) and state > spareStates[slot]:
            if state in self.transitions or state in self.leafs:
                rmap[state] = spareStates[slot]
                if state in self.transitions:
                    self.transitions[spareStates[slot]] = self.transitions[state]
                    del self.transitions[state]
                if state in self.leafs:
                    self.leafs[spareStates[slot]] = self.leafs[state]
                    del self.leafs[state]
                slot  += 1
                state -= 1
            else:
                state -= 1

        for tk in self.transitions:
            for vk in self.transitions[tk]:
                old = self.transitions[tk][vk]
                if old in rmap:
                    self.transitions[tk][vk] = rmap[old]

        self.stateSize = top - len(spareStates)

        return self

    def _trimNonTerminatingStates(self):
        ''' Remove states that do not support a leaf node.

        That is, a leaf node anywhere in the subtree of the state.
        '''
        # need to build inverse state directory
        imap = self._inverseStateDirectory()

        # remove redundant states
        for ts in range(self.stateSize):
            self._testOrRemoveState(ts, imap)

        return self

    def _testOrRemoveState(self, ts, imap):
        ''' If a state has no transitions or values, remove it.

        Checks if a state has any transitions or value, if remove it
        then test recursively down the chain toward root.

        Params:
            ts     test state to check
            imap   inverse state map - state->parent
        '''

        #terminate if the state is useful, otherwise remove the state
        useful = False
        if ts in self.transitions:
            if len(self.transitions[ts]) > 0:
                useful = True
            else:
                del self.transitions[ts]

        if ts in self.leafs:
            if len(self.leafs[ts]) > 0:
                useful = True
            else:
                del self.leafs[ts]

        if useful:
            return

        # if at root, nothing below
        if ts == 0:
            return

        # state has been removed here, or perhaps earlier,
        # remove transition to state if in map
        if ts not in imap:
            return

        # if transaction to state has already gone (probably cleaned recursively
        if imap[ts][0] not in self.transitions:
            return
        if imap[ts][1] not in self.transitions[imap[ts][0]]:
            return

        #otherwise remove transition to this state state
        del self.transitions[imap[ts][0]][imap[ts][1]]

        #then check if source needs to be removed
        self._testOrRemoveState(imap[ts][0], imap)

    #**************************************************************************
    #      Static Range Helpers
    #**************************************************************************


def _equalRanges(left, right):
    ''' Check if the ranges in two rangeLists in normal form are equal.
    '''
    if left == right:
        return True
    return False


def _normaliseRanges(rangeList):
    ''' Normalise rangelist in place.

        Normal form is that the ranges are ordered, no overlaps and no two
        ranges contain consecutive values. Note that all processing assumes
        normal form.
    '''
    l = len(rangeList)
    if l < 2:
        return rangeList
    rangeList.sort()
    d  = 1
    while d < l:
        b = d - 1
        d_last = rangeList[b].last
        if d_last + 2 > rangeList[d].first:
            d1_last = rangeList[d].last
            # merge range into existing result
            if d1_last > d_last:
                newRange = Range(rangeList[b].first, d1_last)
            else:
                newRange = Range(rangeList[b].first, d_last)
            rangeList[b] = newRange
            del rangeList[d]    # s not changed but now indexes next
            l -= 1
        else:
            d += 1
    return rangeList


def _intersectRanges(left, right):
    ''' Intersect two rangelists.
    '''
    rmap = _buildRangeMap(left, right)

    res = []
    start = 0
    mode = 'off'
    for i in range(len(rmap)):
        op = rmap[i][1]
        if mode == 'off':
            if op in [0, 2]:
                mode = 'one'
        elif mode == 'one':
            if op in [0, 2]:
                mode = 'both'
                start = rmap[i][0]
            else:
                mode = 'off'
        elif mode == 'both':
            if op in [1, 3]:
                mode = 'one'
                if rmap[i][0] > start:
                    # if not overlap was exactly zero
                    res.append(Range(start, rmap[i][0] - 1))
    return res


def _intersectRangesWithValues(rangeList, values):
    ''' Return any values present in both values and rangelist.

    Takes a list of values and returns a list containing any values
    which are in the specified rangeList.

    Assumes that the rangelist is normalised
    '''
    if len(values) == 0 or len(rangeList) == 0:
        return []
    tst = sorted(values)
    res = []
    vi = 0
    ri = 0
    while vi < len(tst) and ri < len(rangeList):
        if tst[vi] >= rangeList[ri].first:
            # may be in this range
            if tst[vi] > rangeList[ri].last:
                #above this range
                ri += 1
            else:
                #inside range
                res.append(tst[vi])
                vi += 1
        else:
            #below this range
            vi += 1
    return res


def _differenceRanges(left, right):
    ''' Return the set difference between left and right ranges (left - right)
    '''
    rmap = _buildRangeMap(left, right)

    res = []
    start = 0
    mode = 'off'
    for i in range(len(rmap)):
        op = rmap[i][1]
        if mode == 'off':
            if op == 0:
                mode  = 'on'
                start = rmap[i][0]
            elif op == 2:
                mode  = 'block'
        elif mode == 'block':
            if   op == 0:
                mode  = 'wait'
            elif op == 3:
                mode  = 'off'
        elif mode == 'wait':
            if   op == 1:
                mode  = 'block'
            elif op == 3:
                mode  = 'on'
                start = rmap[i][0]
        else:
            # mode == 'on'
            if   op == 1:
                mode  = 'off'
                res.append(Range(start, rmap[i][0] - 1))
            if   op == 2:
                mode  = 'wait'
                if rmap[i][0] > start:
                    # otherwise both started together
                    # and a value should not be written
                    res.append(Range(start, rmap[i][0] - 1))
    return res


def _hashRangeList(rangeList, depth):
    ''' Return a hash of the elements of the rangelist, including tree depth
    '''
    res = 104729
    for r in rangeList:
        res = (r.first * 257 + r.last * 997 + res * 104729) % RANGE_HASH_FIELDSIZE
    res = hash(depth + res  * 997)  % RANGE_HASH_FIELDSIZE
    return res


def _buildRangeMap(left, right):
    ''' Return a list of tuples that map the two provided ranges together.
    Each tuple is (index,code)
    code: 0:r-start 1:r-end 2-l start 3-r-end (nb end is index FOLLOWING last)
    '''
    res = []
    for r in left:
        res.append((r.first, 0))
        res.append((r.last + 1, 1))
    for r in right:
        res.append((r.first, 2))
        res.append((r.last + 1, 3))
    return sorted(res)

#****************************************************************************
#    State and transition Helpers
#****************************************************************************


def _mapStates(left, right):
    '''Build a dictionary of states in right -> states in left.

    States in right which cannot be identified with any in left are mapped to
    new state numbers above the current highest state index in left.

    Returns:
        a tuple (new state size for left, map)
    '''
    cmap     = {0: 0}
    newStateSize = left.stateSize

    # map states from right to either left states or new states
    toDo = sorted(right.transitions)
    while len(toDo) > 0:
        nextWork = []
        for rtk in toDo:
            rtrans = right.transitions[rtk]
            if rtk not in cmap:
                # not yet mapped
                nextWork.append(rtk)
            elif cmap[rtk] >= left.stateSize:
                # source state is not in new map,
                # so map out children to new states
                for vk in rtrans:
                    cmap[rtrans[vk]] = newStateSize
                    newStateSize += 1
            elif cmap[rtk] in left.transitions:
                # source state maps to a destination state with transitions,
                # so need to check if any are equal
                ltrans = left.transitions[cmap[rtk]]
                for vk in rtrans:
                    if vk in ltrans:
                        #match found so can merge child states
                        #start states == and transition == => next state ==
                        cmap[rtrans[vk]] = ltrans[vk]
                    else:
                        #not found so child state is new
                        cmap[rtrans[vk]] = newStateSize
                        newStateSize += 1
            else:
                # source maps to destination state with no transitions
                # so map out all children
                for vk in rtrans:
                    cmap[rtrans[vk]] = newStateSize
                    newStateSize += 1
            toDo = nextWork
    return (newStateSize, cmap)


def _checkEncoding(class1, class2):
    if class1.encoding != class2.encoding:
        raise ValueError('CharClass: attempt to combine character classes compiled for different encodings')

#***************************************************************************
#    Public Module methods
#***************************************************************************


def newClassFromList(encoding, sourceList):
    ''' Build a new class as the union of the named character classes.

    Failure is silent, since some encodings will not have all listed classes.
    Up to caller to check all present if required.
    '''
    res = CharClass(encoding)
    if len(sourceList) == 0:
        return res
    cc  = CharClass(encoding)
    for charPath in sourceList:
        cc  = CharClass(encoding)
        try:
            cc.loadFromFile(charPath)
            res.union(cc)
        except FileNotFoundError:
            pass
    return res


def newCasedCharacter(cases, encoding, character, ignoreCase):
    ''' Build a single character class from either an integer or a string.

    If the string is several code points it will be treated as a graphene
    sequence (eg CR LF) and built as a single character; case processing
    will not be used.

    Otherwise (for a single character or an integer character) if ignoreCase is
    True then the case file is used to merge alternative cases into the class.
    The case file contains circular refs which are usually 2 long, but may be 3
    '''
    cString = character
    if not isinstance(cString, str):
        cString = chr(character)

    cc = CharClass(encoding)
    cc.loadFromCharacter(cString)
    if len(cString) > 1:
        return cc

    if ignoreCase and cString in cases:
        nextChar = cases[cString]
        while nextChar != cString:
            cn = CharClass(encoding)
            cn.loadFromCharacter(nextChar)
            cc.union(cn)
            nextChar = cases[nextChar]
    return cc


def getAny(encoding):
    '''Return the 'any' character set: all possible encoded codepoints.
    '''

    # is the cc cached?
    if encoding in __allCharacters:
        return __allCharacters[encoding].clone()

    # is the cc compiled in the unicode database?
    try:
        cc = CharClass(encoding)
        cc.loadFromFile(os.path.join(__compilePath, encoding, 'any'))
        if not cc.isEmpty():
            __allCharacters[encoding] = cc
            return cc.clone()
    except:
        pass

    # otherwise need to build the class from scratch
    cc = CharClass(encoding)
    cc.loadFromRange(0, 0x10FFFF)
    __allCharacters[encoding] = cc
    return cc.clone()
