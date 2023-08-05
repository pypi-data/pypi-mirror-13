'''
RE character class compiler for the jsre virtual machine.

@author: Howard Chivers

Copyright (c) 2015, Howard Chivers
All rights reserved.

'''
import logging
import itertools

from jsre.ucd import isEncodingInstalled, getCaseFolding, getPropertyValueNames, getClassPath
from jsre.ucd import ENCODING_STRIDE
from jsre.charclass import CharClass, newCasedCharacter
from jsre.reparser import ReComponent, syntaxError, ACTION_LOOKUP

from jsre.reparser import TYPE_GROUP, TYPE_CLASS, TYPE_CHAR, TYPE_HEX, TYPE_PROPERTY, TYPE_DOT
from jsre.reparser import TYPE_PROG, TYPE_ALT, TYPE_REPEAT, TYPE_RELATION, TYPE_CLASSREF, TYPE_AUXCHARS
from jsre.reparser import TYPE_COMPILED, TYPE_CHARCLASS
from jsre.reparser import AT_COMBINE_AND, AT_COMBINE_DIFF, AT_DISJOINT, AT_B_NODE, AT_NOT, AT_ANY, AT_DOT, AT_NOTCONSUME
from jsre.reparser import IGNORECASE, MULTILINE, DOTALL
from jsre.reparser import VM_MAX_STATE_SIZE
from jsre.reparser import PROG_TEXT_START, PROG_TEXT_END, PROG_BUFF_START, PROG_BUFF_END, PROG_WBOUNDARY
from jsre.reparser import PROG_NWBOUNDARY, PROG_GRAPHEME

dfaLog = logging.getLogger("char_dfa")

# dfa control constants
ROOT_SCAN_LENGTH    = 3        # number of characters in look-ahead scan  
B_TREE_SCAN_LENGTH  = 5        # number of characters in B-tree indexes
B_TREE_SPAN         = 4        # spanning size of Btree node (used for large character alts)

# action type -> (   (internalNmae, property (value, value...), allowEmpty), ...)
AUX_REQUIRES        = {PROG_WBOUNDARY: (('{=word}', '', ('word',), False),
                                        ('{=not_word}', '', ('not_word',), False)
                                        ),
                       PROG_NWBOUNDARY: (('{=word}', '', ('word',), False),
                                        ('{=not_word}', '', ('not_word',), False)
                                        ),
                       PROG_TEXT_START: (('{=newline}', '', ('newline',), False),),
                       PROG_TEXT_END:   (('{=newline}', '', ('newline',), False),),
                       PROG_GRAPHEME:   (('{grapheme_cluster_break=cr}', 'gcb', ('cr',), False),
                                         ('{grapheme_cluster_break=lf}', 'gcb', ('lf',), False),
                                         ('{grapheme_cluster_break=control_cr_lf}', 'gcb', ('control', 'cr', 'lf'), False),
                                         ('{grapheme_cluster_break=l}', 'gcb', ('l',), False),
                                         ('{grapheme_cluster_break=l_v_lv_lvt}', 'gcb', ('l', 'v', 'lv', 'lvt'), False),
                                         ('{grapheme_cluster_break=lv_v}', 'gcb', ('lv', 'v'), False),
                                         ('{grapheme_cluster_break=v_t}', 'gcb', ('v', 't'), False),
                                         ('{grapheme_cluster_break=lvt_t}', 'gcb', ('lvt', 't'), False),
                                         ('{grapheme_cluster_break=t}', 'gcb', ('t',), False),
                                         ('{grapheme_cluster_break=regional_indicator}', 'gcb', ('regional_indicator',), False),
                                         ('{grapheme_cluster_break=extend}', 'gcb', ('extend',), False),
                                         ('{grapheme_cluster_break=spacingmark}', 'gcb', ('spacingmark',), False),
                                         ('{grapheme_cluster_break=prepend}', 'gcb', ('prepend',), True),
                                         ('{=any}', '', ('any',), False)),
                       'CHAR_DOT':      (('{=newline}', '', ('newline',), False),)
                      }


class CharacterCompiler():
    '''Compile characters and character classes in a parse tree into the vm.

    This class takes a parse tree and converts all the characters & character
    classes to compiled character classes.
    Any required classes may then be added to the vm.

    This class configures the state and transition tables in the vm.

    NOTE that this class keeps a directory of what has been compiled to the VM
    and will re-use characters/classes where possible. The character
    compilation process is in two parts; the first returns a tree with ready
    to publish but not linked to the VM. The second allows writing to the VM
    and the class cache.
    This allows recovery of the parsed compiled tree if the VM is full - the
    intermediate result can be loaded into a different vm if necessary.
    '''

    def __init__(self, virtualMachine):
        ''' Initialise character compiler with specific virtual, machine.
        '''
        self.tvm      = virtualMachine
        # the character registry is a dictionary   encoding -> entry
        # where entry is a dictionary    pattern  -> virtual machine state
        #                           or   VM State -> characterClass object
        self.registry  = {}

        # the character cache stores named character classes as they are loaded
        # file reference -> character class

        self.charCache = {}

    def compileCharacters(self, parseRoot, enc_norm, flags, doNotPublish=False):
        ''' Compile a parse tree with a given encoding.

        This returns a tree populated with character classes in published graph
        form. It does not write to allow a choice of vm (ie start a new one if
        one is full). The tree provided as a parameter is not modified (to
        allow one parsed re to be used with many encodings.)

        Params:
            parseRoot   the root of the parse tree
            encodng     a standard (and installed) python codec string
            ignoreCase  if true normal characters (not ranges) match all cases
            doNotPublish instructs edit while character classes are trees
                        primarily for testing publish logic

        Returns:
            The root of a new character-compiled tree
            The tree should contain only types:  GROUP, ALT, PROG, REPEAT
            and CHARCLASS
            Root has attribute 'auxChars' whose children provide extra dfts for programs etc.

        Raises:
            ValueError if the specified encoding is not installed
            SyntaxError for likely errors in the re, or for re elements not
                compatible with the encoding
            SystemError which indicates a bug resulting in an invalid
                data structure
        '''

        multiLine       = True if flags & MULTILINE  else False
        self.ignoreCase = True if flags & IGNORECASE else False
        dotall          = True if flags & DOTALL else False

        self.root          = parseRoot.clone()
        self.root.auxChars = ReComponent(0, TYPE_AUXCHARS)

        # check encoding
        self.encoding   = enc_norm
        if not isEncodingInstalled(enc_norm):
            msg = "Requested encoding requires {} which is not installed.".format(enc_norm)
            dfaLog.error(msg)
            raise ValueError(msg)

        self.root.encoding = self.encoding
        if self.encoding not in self.registry:
            self.registry[self.encoding] = {}

        # add required stride
        if self.encoding in ENCODING_STRIDE:
            self.root.stride = ENCODING_STRIDE[self.encoding]
        else:
            self.root.stride = 1

        self.encReg  = self.registry[self.encoding]

        # rewrite any dot nodes into normal properties
        # (here parse is independent of dotall flag)
        for comp in self.root.filteredBy(TYPE_DOT):
            if dotall:
                value = 'any'
                comp.attr |= AT_ANY
            else:
                value = 'dot_any'
                comp.attr |= AT_DOT
                self._loadAuxCharacters(comp.start, 'CHAR_DOT')
            props = getPropertyValueNames(None, value)
            if props == None:
                msg = 'System Error, property value for %s not in UCD namespace'.format(value)
                dfaLog.error(msg)
                raise SystemError(msg)
            comp.type       = TYPE_PROPERTY
            comp.pattern    = "{" + props[0] + "=" + props[1] + "}"
            comp.uproperty  = props[0]
            comp.uvalue     = props[1]

        # update tree with any character classes already in registry
        # and replace duplicate classes with references
        # this will apply only to outer character classes
        self.classRefRegistry = {}
        self._minimiseClassesToProcess(self.root)

        # Replace leaf characters with character classes
        cases = getCaseFolding()
        for _, comp in self.root:
            if comp.type == TYPE_HEX:
                # hex bytes are byte encoded regardless of encoding
                cc = CharClass(self.encoding)
                cc.loadByteRange(comp.first, comp.last)
                comp.update(TYPE_CHARCLASS, cc)

            elif (comp.type & (TYPE_CHAR | TYPE_HEX)):
                if comp.first == comp.last:
                    # insert single character, with case folding if required
                    comp.update(TYPE_CHARCLASS,
                                newCasedCharacter(cases, self.encoding,
                                                      comp.first,
                                                      self.ignoreCase))
                else:
                    # character range, no need for case folding
                    comp.update(TYPE_CHARCLASS,
                                CharClass(self.encoding,
                                              ifirstChar=comp.first,
                                              ilastChar=comp.last))
                if comp.ref.isEmpty():
                    dfaLog.warning("Character ({}) null in encoding({})class, replaced by void match".format(comp.pattern, self.encoding))

            elif (comp.type & TYPE_PROPERTY):
                # named unicode property
                cc = self._getPropertyClass(False, comp.uproperty, comp.uvalue)
                if AT_NOT & comp.attr:
                    cc.inverse()
                elif comp.uvalue == 'any':
                    comp.attr |= AT_ANY
                comp.update(TYPE_CHARCLASS, cc)

        # eliminate all relation/class nodes by merging character classes
        toDo = list(self.root.filteredBy(TYPE_CLASS | TYPE_RELATION))

        # loop until all nodes joined
        while len(toDo) > 0:
            # get class join which is ready to merge
            wkg = None
            for comp in toDo:
                for child in comp.childList:
                    wkg = comp
                    if child.type != TYPE_CHARCLASS:
                        # child not set - cannot combine here
                        wkg = None
                        break
                if wkg != None:
                    break
            if wkg == None:
                # should be impossible to fail to find one to do
                raise SystemError("CharacterCompiler: Inconsistent Class Tree")

            # do the join
            if wkg.type == TYPE_CLASS:
                cc = CharClass(self.encoding)
                for child in wkg.childList:
                    cc.union(child.ref)
                if wkg.attr & AT_NOT:
                    cc.inverse()

            elif wkg.type == TYPE_RELATION:
                # token is a relation
                cc = wkg.childList[0].ref
                if wkg.attr & AT_COMBINE_AND:
                    cc.intersect(wkg.childList[1].ref)
                elif wkg.attr & AT_COMBINE_DIFF:
                    cc.difference(wkg.childList[1].ref)
                else:
                    raise SystemError("CharacterCompiler: Invalid Relation type")
            else:
                raise SystemError("CharacterCompiler: Invalid class joining type")

            # then update the working node
            wkg.update(TYPE_CHARCLASS, cc)
            toDo.remove(wkg)

        # at this point tree nodes should have only types:
        # GROUP, ALT, PROG. REPEAT, COMPILED, CLASSREF and characters in CHARCLASS

        # find any void character specifications,
        # issue a warning and delete the related tree parent
        if self._nodeIsVoid(self.root):
            msg = "Regular Expression is void under encoding {}".format(self.encoding)
            dfaLog.error(msg)
            raise SyntaxError(msg)

        # prog updates
        for comp in self.root.filteredBy(TYPE_PROG):
            # load any extra compiled characters required by prog types
            self._loadAuxCharacters(comp.start, comp.action)

            # if not multiline, convert text start/end programs to buff start/end
            if not multiLine:
                if comp.action == PROG_TEXT_START:
                    comp.action = PROG_BUFF_START
                if comp.action == PROG_TEXT_END:
                    comp.action = PROG_BUFF_END

        # build lookAhead links to next expression in RE sequence
        self._annotateLookAhead(self.root, None)

        # only for test use
        if doNotPublish:
            return self.root

        # compact characters into graphs
        for comp in itertools.chain(self.root.filteredBy(TYPE_CHARCLASS), self.root.auxChars.filteredBy(TYPE_CHARCLASS)):
            comp.tmpCharClass = comp.ref.clone()  # may need later for registry
            comp.ref.publishToGraph()

        return self.root

    def writeCharactersToVM(self, root):
        ''' Write characters to vm and the internal character cache.

        This updates the root tree in place.

        Additional optimiser characters are added if machine space
        (if not a warning is logged)

        Raises:
            MemoryError which indicates that the VM had insufficient space
            for the compiled characters
        '''
        self.root = root
        self.encoding = root.encoding

        # write to VM, no need to compress to graph here
        for comp in itertools.chain(self.root.filteredBy(TYPE_CHARCLASS), self.root.auxChars.filteredBy(TYPE_CHARCLASS)):
            if comp.pattern in self.registry[self.encoding]:
                # already in vm
                charIndex = self.registry[self.encoding][comp.pattern]
            else:
                # check space remaining
                if comp.ref.getStateSize() >= (VM_MAX_STATE_SIZE - self.tvm.nextState()):
                    msg = "This RE is too big for space remaining in virtual machine"
                    dfaLog.error(msg)
                    raise MemoryError(msg)

                # need to add character class to vm
                charIndex = comp.ref.publishToVM(self.tvm)
                if charIndex == None:
                    raise SystemError("Virtual Machine state allocation failed")
                self.registry[self.encoding][comp.pattern] = charIndex
                self.registry[self.encoding][charIndex]    = comp.tmpCharClass
            del(comp.tmpCharClass)
            comp.update(TYPE_COMPILED, charIndex)

        # point any referenced character classes to the correct compiled object
        for _, comp in self.root:
            if hasattr(comp, 'childList'):
                for i, child in enumerate(comp.childList):
                    if child.type == TYPE_CLASSREF:
                        comp.childList[i] = self.classRefRegistry[child.pattern]

        # identify any loops whose next character (after loop) is disjoint with the loop body
        # this also annotates with simple decision characters where possible
        self._annotateDisjointRepeats()

        # try to build a scan character for root
        # if possible scans are for the first 3 characters in the re
        charIndex = self._publishPreview(self._getPreview(self.root, ROOT_SCAN_LENGTH))
        if charIndex != None:
            self.root.previewDFA = charIndex

        # build B-trees of any alt words sequences and index alt children
        self.root.altDirectory = {}  # altIndex -> word pattern
        for comp in self.root.filteredBy(TYPE_ALT):
            self._buildAltTrees(comp)

    def _loadAuxCharacters(self, start, action):
        ''' Load auxiliary characters

        auxiliary characters are those not within the re are needed as
        dfts to implement re functions such as boundary testing

        This is table driven:
            action -> (spec, spec ...)
            spec = (internalname, property (value, value ...))

        characters are added as children of the root auxChars attribute
        and a childIndex is added to the action comp to index the new children
        '''
        if action not in AUX_REQUIRES:
            return

        auxChars = self.root.auxChars
        if not hasattr(auxChars, 'childList'):
                auxChars.childList = []
                auxChars.childIndex = {}

        for prop in AUX_REQUIRES[action]:
            if prop[0] in auxChars.childIndex:
                continue
            newChild         = ReComponent(start, TYPE_CHARCLASS)
            newChild.pattern = prop[0]
            newChild.ref     = CharClass(self.encoding)
            for value in prop[2]:
                props = getPropertyValueNames(prop[1], value)
                cc = self._getPropertyClass(prop[3], *props)
                if cc.isEmpty() and not prop[3]:
                    syntaxError(self.root.pattern,
                                start,
                                'Syntax error: unable to load characters required for {}'.format(ACTION_LOOKUP[action]))
                newChild.ref.union(cc)
            auxChars.childIndex[prop[0]] = newChild
            auxChars.childList.append(newChild)

    def _getPropertyClass(self, silent, prop, value):
        ''' Return a character class built from a unicode property [and value].
        '''
        fileRef  = getClassPath(self.encoding, prop, value)
        if fileRef in self.charCache:
            return self.charCache[fileRef].clone()
        if fileRef == None:
            if not silent:
                dfaLog.warning("Unicode Character class ({},{}) not installed or perhaps null in encoding ({}), replaced by void match".format(prop, value, self.encoding))
            return CharClass(self.encoding)

        cc = CharClass(self.encoding)
        cc.loadFromFile(fileRef)
        self.charCache[fileRef] = cc.clone()
        return cc

    def _nodeIsVoid(self, node):
        ''' Delete void children and check recursively if this is a void node
        '''
        # deal with leaf characters
        if node.type & (TYPE_COMPILED | TYPE_PROG | TYPE_CLASSREF):
            return False

        elif node.type == TYPE_CHARCLASS:
            if node.ref.isEmpty():
                return True
            else:
                return False

        # if any child of a group is void the whole group is void
        elif node.type & (TYPE_GROUP | TYPE_REPEAT):
            for child in node.childList:
                if self._nodeIsVoid(child):
                    if hasattr(child, 'pattern'):
                        dfaLog.warning('Group or Repeat at position {:d} void because of void child: {}'.format(node.start, child.pattern))
                    else:
                        dfaLog.warning('Group or Repeat at position {:d} void because of void child.'.format(node.start))
                    return True
            return False

        # if all nodes of an alt are void, the whole alt is void
        elif node.type & TYPE_ALT:
            newChildList = []
            for child in node.childList:
                if not self._nodeIsVoid(child):
                    newChildList.append(child)
            if len(newChildList) == 0:
                dfaLog.warning('Alt at position {:d} void because of void children.'.format(node.start))
                return True
            else:
                node.childList = newChildList
                return False

        else:
            raise SystemError("Invalid node remains in compiled parse tree: {:d}".format(node.type))

    def _annotateLookAhead(self, comp, lookAhead):
        ''' Build lookAhead attributes for groups, where possible.

        This searches for the next element in the re sequence and annotates
        components accordingly.
        '''
        if not hasattr(comp, 'childList'):
            return

        for i, child in enumerate(comp.childList):
            # next component is next child unless ALT
            # in which case next is the inherited lookahead
            # ie the next to the highest placed ALT (if nested)
            if i < len(comp.childList) - 1 and comp.type != TYPE_ALT:
                child.lookAhead = comp.childList[i + 1]
            else:
                child.lookAhead = lookAhead
            self._annotateLookAhead(child, child.lookAhead)

    def _annotateDisjointRepeats(self):
        ''' annotate optional repeat groups if disjoint from next character

        Repeat groups are given the attribute AT_DISJOINT if it can be
        established that the repeat expression is disjoint from the lookahead.
        No lookahead present also implies disjoint,
        Lookahead to a prog (zero width test) is never disjoint.
        '''

        for comp in self.root.filteredBy(TYPE_REPEAT):
            #does loop have a character body?
            if not (comp.childList[0].type & (TYPE_COMPILED | TYPE_CHARCLASS)):
                continue

            # no valid lookahead set, always disjoint
            #if (not hasattr(comp, 'lookAhead')) or (comp.lookAhead == None):
            #    comp.attr |= AT_DISJOINT
            # DEBUG was elif
            if hasattr(comp, 'lookAhead') and (comp.lookAhead != None):
                # not possible to lookahead through zero width program
                if comp.lookAhead.type & TYPE_PROG:
                    continue

                # get lookahead character class
                lookAhead = self._getPreview(comp.lookAhead, 1)
                if lookAhead == None:
                    continue

                # need to check if lookahead is disjoint valid lookahead character
                body_cc = comp.childList[0].ref if type(comp.childList[0].ref) is CharClass else self.registry[self.encoding][comp.childList[0].ref]
                test_cc = body_cc.clone()
                test_cc.intersect(lookAhead[0])
                if test_cc.isEmpty():
                    comp.attr |= AT_DISJOINT

    def _getPreview(self, comp, length):
        '''
        the scanlength is the maximum list length returned
        the actual length returned depends on characters found
        '''

        self.maxPreviewLength     = length
        _, valid, preview = self._buildPreview(comp)

        # trim list if necessary
        if preview[0] == None or preview[0].isEmpty() or valid == 0:
            return None
        for i in range(len(preview) - 1, 0, -1):
            if preview[i] == None or preview[i].isEmpty() or valid <= i:
                del(preview[i])
            else:
                break
        return preview

    def _buildPreview(self, comp):
        ''' returns a component's preview (list of CharClass objects)
            and the length of the shortest valid word and the longest
            possible position at which a new word should be added.
            (long, valid, preview)
        '''
        if comp.type == TYPE_CLASSREF:
            return self._buildPreview(comp.ref)

        elif comp.type == TYPE_COMPILED:
            preview = [None] * self.maxPreviewLength
            preview[0] = self.registry[self.encoding][comp.ref].clone()
            return 1, 1, preview

        elif comp.type == TYPE_ALT:
            if hasattr(comp, 'scanToPublish'):
                #component has a cached preview
                preview = [None] * self.maxPreviewLength
                for i, cl in enumerate(comp.scanToPublish):
                    preview[i] = cl.clone()
                l = len(comp.scanToPublish)
                return l, l, preview

            #normal process - no cache
            long, valid, preview   = self._buildPreview(comp.childList[0])
            for i in range(1, len(comp.childList)):
                nl, nv, np = self._buildPreview(comp.childList[i])
                self._joinPreview(preview, np, 0, 0)
                valid = min(valid, nv)
                long  = max(long, nl)
            return long, valid, preview

        elif comp.type == TYPE_GROUP:
            long, valid, preview   = self._buildPreview(comp.childList[0])
            for i in range(1, len(comp.childList)):
                nl, nv, np = self._buildPreview(comp.childList[i])
                self._joinPreview(preview, np, valid, long)
                valid += nv
                long  += nl
            if comp.attr & AT_NOTCONSUME:
                valid = 0
                long  = 0
            return long, valid, preview

        elif comp.type == TYPE_REPEAT:
            lchild, vchild, pchild   = self._buildPreview(comp.childList[0])
            preview = [None] * self.maxPreviewLength
            valid  = 0
            long   = 0

            # required repeats, like group
            rep = comp.repeatMin if comp.repeatMin <= self.maxPreviewLength else self.maxPreviewLength
            for _ in range(rep):
                self._joinPreview(preview, pchild, valid, long)
                valid += vchild
                long  += lchild

            # optional repeats (star)
            if comp.repeatMax > 0:
                opt = comp.repeatMax - rep if comp.repeatMax - rep <= self.maxPreviewLength else self.maxPreviewLength
                long += opt
                self._joinPreview(preview, pchild, valid, long)

            return long, valid, preview

        else:
            # progs too difficult
            preview = [None] * self.maxPreviewLength
            return 0, 0, preview

    def _previewLen(self, preview):
        ''' returns current length of preview
        '''
        lp = len(preview)
        for i in range(lp):
            if preview[i] == None:
                return i
        return lp

    def _joinPreview(self, dest, src, first, last):
        ''' join two previews add source to destination at every position from
            first to last inclusive.
        '''
        for start in range(first, last + 1):
            for sourceIndex in range(self._previewLen(src)):
                posn = start + sourceIndex
                if posn >= self.maxPreviewLength:
                    break
                if src[sourceIndex] == None:
                    break
                if dest[posn] == None:
                    dest[posn] = src[sourceIndex].clone()
                else:
                    dest[posn].union(src[sourceIndex])
        return dest

    def _publishPreview(self, preview):
        ''' compress a preview into a single published character then write to VM
            returns VM character index if OK, else None
        '''
        if preview == None:
            return None

        # compress to a single character
        preview[0].publishToGraph()
        for i in range(1, len(preview)):
            preview[i].publishToGraph()
            preview[0].addAsSequence(preview[i])
        compiledSize = preview[0].getStateSize()
        if compiledSize >= (VM_MAX_STATE_SIZE - self.tvm.nextState()):
            dfaLog.warning("Insufficient VM State size remaining ({:d}) to write optimiser characters, require ({:d})".format(VM_MAX_STATE_SIZE - self.tvm.nextState(), compiledSize))
            return None

        charIndex = preview[0].publishToVM(self.tvm)
        if charIndex == None:
            raise SystemError("Virtual Machine state allocation failed when writing scan characters")
        return charIndex

    def _buildAltTrees(self, comp):
        ''' builds an ALT B-tree and adds scan characters to alts

        expects that the component param is of type alt
        scanToPublish allows scan previews to be cached bottom up
        '''

        if comp.attr & AT_B_NODE or hasattr(comp, 'previewDFA'):
            # already done
            return

        # build scan characters for alt children
        for child in comp.childList:
            charIndex = self._getPreview(child, B_TREE_SCAN_LENGTH)
            if charIndex != None:
                child.scanToPublish = charIndex

        if len(comp.childList) > (B_TREE_SPAN * 3) // 2:
            # build a B tree

            # sort list to make keys more effective
            if self.ignoreCase:
                comp.childList.sort(key=lambda gp: gp.pattern.lower())
            else:
                comp.childList.sort(key=lambda gp: gp.pattern)

            # build b-tree
            while len(comp.childList) > (B_TREE_SPAN * 3) // 2:
                newList = []
                for i in range(0, len(comp.childList), B_TREE_SPAN):
                    newList.append(self._newAltFromList(i, comp.childList, comp.start))
                comp.childList = newList

        # build a decision character at the top level if possible
        charIndex = self._publishPreview(self._getPreview(comp, B_TREE_SCAN_LENGTH))
        if charIndex != None:
            comp.previewDFA = charIndex

        # publish decision characters
        for _, node in comp:
            if hasattr(node, 'scanToPublish'):
                if not hasattr(node, 'previewDFA'):
                    charIndex = self._publishPreview(node.scanToPublish)
                    if charIndex != None:
                        node.previewDFA = charIndex
                del(node.scanToPublish)

    def _newAltFromList(self, pos, listWords, start):
        ''' build a new alt which is a B-tree node with index range decision character
        '''
        newComp = ReComponent(start, TYPE_ALT)
        newComp.attr |= AT_B_NODE
        for i in range(pos, pos + B_TREE_SPAN):
            newComp.childList.append(listWords[i])
            if i == len(listWords) - 1:
                break
        charIndex = self._getPreview(newComp, B_TREE_SCAN_LENGTH)
        if charIndex != None:
            newComp.scanToPublish = charIndex
        return newComp

    def _minimiseClassesToProcess(self, comp):
        ''' replaces classes with references and compiled where
            possible (can only do top level classes)
        '''
        if not hasattr(comp, 'childList'):
            return

        for child in comp.childList:
            if child.type == TYPE_CLASS:
                if child.pattern in self.encReg:
                    # update tree with compiled character from registry
                    child.update(TYPE_COMPILED, self.encReg[child.pattern])
                elif child.pattern in self.classRefRegistry:
                    # update tree with a reference to another class
                    child.update(TYPE_CLASSREF, self.classRefRegistry[child.pattern])
                else:
                    # class not already known, register pattern
                    self.classRefRegistry[child.pattern] = child
            else:
                # not a class, process children if present
                self._minimiseClassesToProcess(child)

