'''
This module compiles re programs for the jsre virtual machine.

@author: Howard Chivers

Copyright (c) 2015, Howard Chivers
All rights reserved.

'''

import logging
from jsre.reparser import TYPE_GROUP, TYPE_ALT, TYPE_PROG, TYPE_REPEAT, TYPE_COMPILED, VM_COUNT_UNMEASURED
from jsre.reparser import AT_NOTCAPTURE, AT_NOTCONSUME, AT_NOTGREEDY, AT_DISJOINT, AT_CONTROLLING, AT_B_NODE
from jsre.reparser import PROG_TEXT_START, PROG_TEXT_END, PROG_BUFF_START, PROG_BUFF_END, PROG_WBOUNDARY, PROG_BACKREFERENCE
from jsre.reparser import PROG_NWBOUNDARY, PROG_GRAPHEME, INDEXALT, SECTOR, XASYNCHRONOUS, XDUMPPROG

compileLog = logging.getLogger("compile")
SUBSTITUTE    = 'substitute'             # program template marker
LOOP_THRESHOLD_FOR_GUARDS = 5            # loops need to be bigger than this to be worth the overhead of guards

# compiler node marker attributes
AT_USED_AS_LOOKAHEAD  = 0x1000
AT_CONTROL_CONSUMED   = 0x2000
AT_START_BUFFER_START = 0x4000
AT_START_LOOP_DOT     = 0x8000
AT_BACKREFERENCED     = 0x10000
#AT_START_LOOP_ANY        Anchor at start of buffer and after publish but not incremented, not safe so discontinued?

# VM configuration
VM_MAX_COUNTERS            =    4        # number of counters allowed
VM_MAX_MARK_PAIRS          =    32       # number of mark pairs allowed
VM_MARK_MASK               = 0xFFFFFFFF  # all mark bits set
VM_MAX_BYTECODE_SIZE       = 49152       # maximum size of bytecode
VM_MAX_GUARDS              = 4096        # just in case a strange re is in danger of overflow

# *******************************************
# VM Instruction Set
# *******************************************

#character transition leaf marker (used in place of destination state for transition)
VM_CHARACTER_OK            = 0xFFFF    # character transition success

#Start Commands
VM_START_SECTOR            = 0x8000    # run offset start anchors
VM_START_FIXED_ANCHOR      = 0x4000    # do not allow anchor to be incremented
VM_START_NOINC_ANCHOR      = 0x2000    # prevent anchor increment unless after publish
VM_START_RESERVED_MATCH    = 0x1000    # highest value mark pair used is reserved for signalling

# byte code instructions - character testing
VM_INSTR_CHARACTER         =   0x20    # a character [group], if set then ...
VM_FLAG_SET_GUARD          =   0x10    # prevent repeat execution of this character test if the test fails
                                       # and no match is achieved from this anchor.
VM_FLAG_ZERO_WIDTH         =   0x8     # do not auto-increment with the character byte width, just test
VM_FLAG_CONTINUE           =   0x4     # a match fail will allow the stream to continue (but not consume bytes) and just set flags
VM_FLAG_PREVIOUS           =   0x2     # test previous character
VM_FLAG_BRANCH             =   0x1     # short forward branch (by index) on character fail


VM_INSTR_TEST              =  0x40     # test instruction. Will branch to address on success. Function is controlled by flags: that follow:
                                       # note that no test flag set = unconditional jump, only FLAG_NOT set -> NOP
VM_FLAG_TEST_NOT           =  0x01     # invert decision action, branch on false
VM_FLAG_TEST_FLAGS         =  0x02     # test VM flags masked by index byte
VM_FLAG_TEST_COUNT         =  0x04     # decrement counter and branch if zero
VM_FLAG_TEST_GUARD         =  0x08     # test if anchor guard is passed
VM_FLAG_TEST_BACK          =  0x10     # backreference test

# other instructions
VM_INSTR_NEW_THREAD        =   0x1     # write temp state to new thread
VM_INSTR_RESET_TO_MARK     =   0x2     # set the byte pointer to the indexed mark
VM_INSTR_SET_COUNT         =   0x3     # set indexed counter to value
VM_INSTR_PUBLISH           =   0x4     # publish (write marked locations to result)
VM_INSTR_SCAN              =   0x5     # use character to scan for next anchor, mark start 0 if OK
VM_INSTR_SET_CONTEXT       =   0x6     # set indexed context (index of FLAG_NOT will reset)
VM_INSTR_SET_MARK          =   0x7     # set indexed mark to value
VM_INSTR_MARK_START        =   0xA     # mark start of re or subgroup
VM_INSTR_MARK_END          =   0xE     # write current byte address to indexed mark
                                       # note if matching context is set this will delete the context from the traceHeap

# instruction special values and flags
VM_VMFL_CHARACTER_OK       = 0x1       # last character test OK
VM_VMFL_START              = 0x2       # at buffer start (not just a new anchor)
VM_VMFL_ANCHOR             = 0x4       # at new anchor
VM_VMFL_END                = 0x8       # at end of buffer
VM_VMFL_PUBLISH            = 0x10      # restarted following publish

# ******************************************************************
#    Program Templates
# ******************************************************************

# note that templates use relative addresses in threads and tests

T_SCAN_NEWLINE       = ((VM_INSTR_TEST | VM_FLAG_TEST_FLAGS, VM_VMFL_START, 4, False),
                        (VM_INSTR_CHARACTER | VM_FLAG_PREVIOUS | VM_FLAG_BRANCH, 1, SUBSTITUTE, False),  # s = newline
                        (VM_INSTR_TEST, 0, 2, False),
                        (VM_INSTR_SCAN, 0, SUBSTITUTE, False),                                   # s = newline
                        (VM_INSTR_CHARACTER | VM_FLAG_BRANCH, 1, SUBSTITUTE, False),             # s = newline
                        (VM_INSTR_TEST, 0, -1, False),
                        (VM_INSTR_MARK_START, 0, 0, False))

T_GROUP_START        = ((VM_INSTR_MARK_START, SUBSTITUTE, 0, False),)
T_GROUP_START_NOTGDY = ((VM_INSTR_SET_CONTEXT, SUBSTITUTE, 0, False),)
T_GROUP_END          = ((VM_INSTR_NEW_THREAD, 0, 1, True),
                        (VM_INSTR_MARK_END, SUBSTITUTE, 0, False))
T_GROUP_RESET        = ((VM_INSTR_RESET_TO_MARK, SUBSTITUTE, 0, False),)

T_JMP_LOOKAHEAD      = ((VM_INSTR_CHARACTER | VM_FLAG_ZERO_WIDTH | VM_FLAG_BRANCH, SUBSTITUTE, SUBSTITUTE, False),
                        (0, 0, 0, 0))

T_ALT_MARK_ID        = ((VM_INSTR_SET_MARK, SUBSTITUTE, SUBSTITUTE, False),)
T_ALT_GUARD          = ((VM_INSTR_TEST | VM_FLAG_TEST_NOT | VM_FLAG_TEST_GUARD, SUBSTITUTE, SUBSTITUTE, False),)

T_LOOP_SET_COUNT     = ((VM_INSTR_SET_COUNT, SUBSTITUTE, SUBSTITUTE, False),)
T_LOOP_TEST          = ((VM_INSTR_TEST | VM_FLAG_TEST_NOT | VM_FLAG_TEST_COUNT, SUBSTITUTE, SUBSTITUTE, False),)
T_LOOP_GUARD         = ((VM_INSTR_TEST | VM_FLAG_TEST_GUARD, SUBSTITUTE, SUBSTITUTE, True),)

T_YIELD              = ((VM_INSTR_NEW_THREAD, 0, 1, True),)

T_PROG_LINESTART     = ((VM_INSTR_TEST | VM_FLAG_TEST_FLAGS, VM_VMFL_START, 3, False),
                        (VM_INSTR_CHARACTER | VM_FLAG_ZERO_WIDTH | VM_FLAG_BRANCH, 0, SUBSTITUTE, True),  # s = newline
                        (VM_INSTR_CHARACTER | VM_FLAG_PREVIOUS, 0, SUBSTITUTE, False))           # s = newline

T_PROG_LINEEND       = ((VM_INSTR_TEST | VM_FLAG_TEST_FLAGS, VM_VMFL_END, 3, False),
                        (VM_INSTR_CHARACTER | VM_FLAG_ZERO_WIDTH, 0, SUBSTITUTE, False),          # s = newline
                        (VM_INSTR_CHARACTER | VM_FLAG_PREVIOUS | VM_FLAG_BRANCH, 0, SUBSTITUTE, True))  # s = newline

T_PROG_BACKREFERENCE = ((VM_INSTR_TEST | VM_FLAG_TEST_BACK, SUBSTITUTE, 1, True),)

T_PROG_WD_BOUND      = ((VM_INSTR_CHARACTER | VM_FLAG_ZERO_WIDTH | VM_FLAG_BRANCH, 3, SUBSTITUTE, False),  # s = \w
                        (VM_INSTR_TEST | VM_FLAG_TEST_FLAGS, VM_VMFL_START, 6, False),
                        (VM_INSTR_CHARACTER | VM_FLAG_PREVIOUS, 0, SUBSTITUTE, False),           # s = \W
                        (VM_INSTR_TEST, 0, 4, False),
                        (VM_INSTR_TEST | VM_FLAG_TEST_FLAGS, VM_VMFL_END, 2, False),
                        (VM_INSTR_CHARACTER | VM_FLAG_ZERO_WIDTH, 0, SUBSTITUTE, False),         # s = \W
                        (VM_INSTR_CHARACTER | VM_FLAG_PREVIOUS, 0, SUBSTITUTE, False))           # s = \w

T_PROG_NOT_WD_BOUND  = ((VM_INSTR_CHARACTER | VM_FLAG_ZERO_WIDTH | VM_FLAG_BRANCH, 2, SUBSTITUTE, False),  # s = \w
                        (VM_INSTR_CHARACTER | VM_FLAG_PREVIOUS, 0, SUBSTITUTE, False),           # s = \w
                        (VM_INSTR_TEST, 0, 5, False),
                        (VM_INSTR_TEST | VM_FLAG_TEST_FLAGS, VM_VMFL_END, 2, False),
                        (VM_INSTR_CHARACTER | VM_FLAG_ZERO_WIDTH, 0, SUBSTITUTE, False),         # s = \W
                        (VM_INSTR_TEST | VM_FLAG_TEST_FLAGS, VM_VMFL_START, 2, False),
                        (VM_INSTR_CHARACTER | VM_FLAG_PREVIOUS, 0, SUBSTITUTE, False))           # s = \W

T_TEST_START         = ((VM_INSTR_TEST | VM_FLAG_TEST_FLAGS, VM_VMFL_START, 1, True),)
T_TEST_END           = ((VM_INSTR_TEST | VM_FLAG_TEST_FLAGS, VM_VMFL_END, 1, True),)

T_JUMP_IF_START      = ((VM_INSTR_TEST | VM_FLAG_TEST_FLAGS, VM_VMFL_START, SUBSTITUTE, False),)
T_JUMP_IF_END        = ((VM_INSTR_TEST | VM_FLAG_TEST_FLAGS, VM_VMFL_END, SUBSTITUTE, False),)

T_FAIL_BETWEEN       = ((VM_INSTR_CHARACTER | VM_FLAG_PREVIOUS | VM_FLAG_BRANCH, 1, SUBSTITUTE, False),
                        (VM_INSTR_CHARACTER | VM_FLAG_ZERO_WIDTH | VM_FLAG_BRANCH, 0, SUBSTITUTE, True))
T_JUMP_IF_AFTER      = ((VM_INSTR_CHARACTER | VM_FLAG_PREVIOUS | VM_FLAG_BRANCH, 1, SUBSTITUTE, False),
                        (VM_INSTR_TEST, 0, SUBSTITUTE, False))
T_JUMP_IF_BEFORE     = ((VM_INSTR_CHARACTER | VM_FLAG_ZERO_WIDTH | VM_FLAG_BRANCH, 1, SUBSTITUTE, False),
                        (VM_INSTR_TEST, 0, SUBSTITUTE, False))
T_FAIL_AFTER         = ((VM_INSTR_CHARACTER | VM_FLAG_PREVIOUS | VM_FLAG_BRANCH, 0, SUBSTITUTE, True),)
T_FAIL_BEFORE        = ((VM_INSTR_CHARACTER | VM_FLAG_ZERO_WIDTH | VM_FLAG_BRANCH, 0, SUBSTITUTE, True),)

T_PREVIOUS           = ((VM_INSTR_CHARACTER | VM_FLAG_PREVIOUS, 0, SUBSTITUTE, False),)
T_CHARACTER          = ((VM_INSTR_CHARACTER, 0, SUBSTITUTE, False),)
T_CHAR_BRANCH        = ((VM_INSTR_CHARACTER | VM_FLAG_BRANCH, SUBSTITUTE, SUBSTITUTE, False),)
T_CHAR_ANCHOR        = ((VM_INSTR_CHARACTER | VM_FLAG_SET_GUARD, 0, SUBSTITUTE, False),)
T_CHAR_ANCHOR_BRANCH = ((VM_INSTR_CHARACTER | VM_FLAG_BRANCH | VM_FLAG_SET_GUARD, SUBSTITUTE, SUBSTITUTE, False),)
T_CHAR_ZERO          = ((VM_INSTR_CHARACTER | VM_FLAG_ZERO_WIDTH | VM_FLAG_BRANCH, SUBSTITUTE, SUBSTITUTE, False),)
T_SCAN               = ((VM_INSTR_SCAN, 0, SUBSTITUTE, False),)
T_LOOKAHEAD          = ((VM_INSTR_CHARACTER | VM_FLAG_ZERO_WIDTH, 0, SUBSTITUTE, False),)
T_PUBLISH            = ((VM_INSTR_PUBLISH, 0, 0, True),)
T_NULL               = ((0, 0, 0, 0),)
T_NOP                = ((VM_INSTR_TEST | VM_FLAG_TEST_NOT, 0, 0, False),)
T_STOP_THREAD        = ((VM_INSTR_TEST | VM_FLAG_TEST_NOT, 0, 0, True),)
T_JUMP               = ((VM_INSTR_TEST, 0, SUBSTITUTE, False),)

# ******************************************************************
#    Compiler
# ******************************************************************


def compileProgram(tvm, tree, flags, offset=0, stride=0):
    '''Compile the program needed for a character-compiled tree.

    This generates a program than writes it to the vm;
    the input tree is annotated but not modified.

    Params:
        tvm         a virtual machine with the referenced characters set
        tree        root of parse tree
        offset      start offset (added to give position in match buffer)
        stride      amount to increment anchor (0 = never, 1 = normal)
        flags       re flags (see parser for declarations)

    Returns:
        tvm is updated with new re
        nameNap    dictionary of group names -> markId
        matchCount number of matches to be returned
        startIndex re index number in the vm (will be key in returned match)

    Raises:
        SyntaxError for REs that are not supported - exceed limits or feature not
                    yet implemented.
    '''
    indexAlts    = True if flags & INDEXALT else False
    sectorMode   = True if flags & SECTOR else False
    asynchronous = True if flags & XASYNCHRONOUS else False
    xprint       = True if flags & XDUMPPROG else False

    # build start type
    _markStartAttributes(tree, tree)
    startCommand = tree.endianMask & 0xF
    if asynchronous:
        tree.stride = 0
    if sectorMode:
        startCommand  |= VM_START_SECTOR
        tree.stride   = stride
    if tree.attr & AT_START_BUFFER_START:
        startCommand  |= VM_START_FIXED_ANCHOR
    if indexAlts:
        startCommand |= VM_START_RESERVED_MATCH

    # number groups, calculate nesting and backreference masks
    returnCount, nameMap, endOrder, backrefMask, subMasks = _numberGroups(tree, indexAlts)

    # mark controlling repeats - ie repeats that the anchor can skip if already tested
    guardCount = _markControllingRepeats(tree, 0)[0]

    # now compile
    compiler = ProgCompiler(tvm, indexAlts, returnCount, nameMap)
    program  = compiler.compileProg(tree)
    if xprint:
        printProgram(program)

    # Offset and Load
    startAddress = tvm.nextProgramAddress()
    if startAddress + len(program) > VM_MAX_BYTECODE_SIZE:
        raise SystemError("Program too big for virtual machine. (Attempting to load additional {:d} from address {:d})".format(len(program), startAddress))
    # convert relative offset to fixed addresses for vm
    for i in range(len(program)):
        instr = program[i]
        if (instr[0] == VM_INSTR_NEW_THREAD) or (instr[0] & VM_INSTR_TEST):
            program[i] = (instr[0], instr[1], instr[2] + startAddress + i, instr[3])
    tvm.newProgram(program)

    #Build start
    startAttribs  = (startCommand, startAddress, returnCount, offset, tree.stride, guardCount, backrefMask, subMasks)
    startIndex = writeStartToVM(tvm, startAttribs)

    return startIndex, returnCount, nameMap, startAttribs, endOrder


def writeStartToVM(tvm, startAttribs):
    ''' Writes the specified start to the VM, returns start index.
    '''
    startIndex = tvm.nextStart()
    tvm.newStart(startIndex, startAttribs)
    return startIndex


class ProgCompiler():

    def __init__(self, tvm, indexAlts, returnCount, nameMap):
        ''' Construct compiler.

        Params:
            tvm          virtual machine
            indexAlts    flag = index top level alts
            returnCount  number of user-sspecified subgroups = first spare group id
            nameMap      groupNames -> group id
        '''
        self.tvm         = tvm
        self.indexAlts   = indexAlts
        self.program     = []
        self.pc          = 0            # program counter
        self.counter     = 0            # index for counters
        self.nextGroup   = returnCount  # first assignable group (mark) index
        self.nameMap     = nameMap      # maps group names to group index
        self.bReturn     = []           # stack for B-node return addresses

        self.typeAction = {TYPE_GROUP: self._cp_group,
                           TYPE_ALT: self._cp_alt,
                           TYPE_PROG: self._cp_action,
                           TYPE_REPEAT: self._cp_repeat,
                           TYPE_COMPILED: self._cp_compiled,
                           }

    def compileProg(self, root):
        ''' main compiler entry
        '''
        self.root = root

        if self.indexAlts:
            self.altMarkIndex = root.altMarkIndex

        # prefix program with scan & anchor control if possible
        if root.attr & AT_START_LOOP_DOT:
            # special scan for start of newline
            self._appendTemplate(T_SCAN_NEWLINE,
                                 root.auxChars.childIndex['{=newline}'].ref,
                                 root.auxChars.childIndex['{=newline}'].ref,
                                 root.auxChars.childIndex['{=newline}'].ref)
        else:
            # normal scan
            if hasattr(root, 'previewDFA'):
                self._appendTemplate(T_SCAN, root.previewDFA)
            else:
                compileLog.info("No fast scan trigger sequence created for this RE")

            # anchor control
            control = self._getControllingRepeat(root)
            if control != None:
                self._appendTemplate(T_LOOP_GUARD, control.guardIndex, 1)

            # add start mark if scan was not possible (scan automatically marks the start)
            if not hasattr(root, 'previewDFA'):
                self._appendTemplate(T_GROUP_START, 0)

        # build the NFA
        self.typeAction.get(root.type, self._cp_unimplemented)(root)

        # finally we can declare success
        # publish must be in separate thread to enforce byte order (greedy/not)
        self._appendTemplate(T_YIELD)
        self._appendTemplate(T_PUBLISH)

        # check for nasties
        for statement in self.program:
            if statement[0] == 0:
                printProgram(self.program)
                raise SystemError("Null instruction in compiled program")

        return self.program

    def _cp_group(self, comp):

        # get group mark is required
        dynamicGroupMark = False
        if (not hasattr(comp, 'markIndex')) and (comp.attr & (AT_NOTCONSUME | AT_NOTGREEDY)):
            comp.markIndex = self._getGroupMarkIndex()
            dynamicGroupMark = True

        # start of group
        if comp.attr & AT_NOTGREEDY:
            self._appendTemplate(T_GROUP_START_NOTGDY, comp.markIndex)
        elif hasattr(comp, 'markIndex') and not (comp.markIndex == 0):
            self._appendTemplate(T_GROUP_START, comp.markIndex)

        # group body
        for child in comp.childList:
            self.typeAction.get(child.type, self._cp_unimplemented)(child)

        # group end
        if comp.attr & AT_NOTCONSUME:
            self._appendTemplate(T_GROUP_RESET, comp.markIndex)
        elif hasattr(comp, 'markIndex'):
            self._appendTemplate(T_GROUP_END, comp.markIndex)

        # release any dynamic index
        if dynamicGroupMark:
            self._freeGroupMarkIndex()

    def _cp_alt(self, comp):
        # insertposn to remember where to put newthread statements
        insertPosn  = []
        for child in comp.childList:
            # decision block to launch childList

            # get lookahead character & anchor controls
            lookAhead = self._getPreview(child)
            control = self._getControllingRepeat(child)

            # add combined character/anchor test if possible
            if control != None and lookAhead >= 0:
                self._appendTemplate(T_ALT_GUARD, control.guardIndex, 3)
                self._appendTemplate(T_CHAR_ZERO, 1, lookAhead)

            # anchor control if possible
            elif control != None:
                self._appendTemplate(T_ALT_GUARD, control.guardIndex, 2)

            # lookahead test
            elif lookAhead >= 0:
                self._appendTemplate(T_CHAR_ZERO, 1, lookAhead)

            # placeholder for new thread
            insertPosn.append(len(self.program))
            self._appendTemplate(T_NULL)

        # normal alt stops here, or b-nodes return to parent thread
        if self._bReturnEmpty():
            self._appendTemplate(T_STOP_THREAD)
        else:
            self._appendTemplate(T_JUMP, self._pop_bReturn() - len(self.program))

        # now write a thread for each child, will be started from above if necessary
        altPosn     = []
        for i, child in enumerate(comp.childList):
            if child.attr & AT_B_NODE:
                # can jump to b-tree nodes, no need for thread
                self.program[insertPosn[i]] = (VM_INSTR_TEST, 0, len(self.program) - insertPosn[i], False)
                # body return
                self._push_bReturn(1 + insertPosn[i])
            else:
                # link alt startup to head of threads
                self.program[insertPosn[i]] = (VM_INSTR_NEW_THREAD, 0, len(self.program) - insertPosn[i], False)
                # mark index if required to identify alt
                if hasattr(child, 'altIndex') and self.indexAlts:
                    self._appendTemplate(T_ALT_MARK_ID, self.altMarkIndex, child.altIndex)
                # add body
            self.typeAction.get(child.type, self._cp_unimplemented)(child)
            altPosn.append(len(self.program))
            self._appendTemplate(T_NULL)

        # all join here
        for i in range(len(altPosn)):
            # terminate the end of each alt group
            self.program[altPosn[i]] = (VM_INSTR_NEW_THREAD, 0, len(self.program) - altPosn[i], True)

    def _cp_compiled(self, comp):
        self._appendTemplate(T_CHARACTER, comp.ref)

    def _cp_repeat(self, comp):

        count = comp.repeatMin
        childIsCharacter = True if comp.childList[0].type == TYPE_COMPILED else False

        # if control repeat, insert guard

        if (comp.attr & AT_CONTROLLING) and not (comp.attr & AT_CONTROL_CONSUMED):
            self._appendTemplate(T_LOOP_GUARD, comp.guardIndex, 1)
        #
        # required repeats first
        #

        # if loop is short and child is a single character, enumerate
        if count > 0 and count < 64 and childIsCharacter:
            for i in range(count):
                if comp.attr & AT_CONTROLLING:
                    self._appendTemplate(T_CHAR_ANCHOR, comp.childList[0].ref)
                else:
                    self._appendTemplate(T_CHARACTER, comp.childList[0].ref)
            count = 0

        # no loop required for just 1, whatever the loop body
        if count == 1 or self._separateControlLoop(comp.childList[0], False):
            self.typeAction.get(comp.childList[0].type, self._cp_unimplemented)(comp.childList[0])
            count -= 1

        # otherwise use counting loop
        if count > 1:

            # init loop counter
            index       = self._getCounter()
            self._appendTemplate(T_LOOP_SET_COUNT, index, count)

            loopHead = len(self.program)

            # loop action
            if comp.attr & AT_CONTROLLING:
                self._appendTemplate(T_CHAR_ANCHOR, comp.childList[0].ref)
            else:
                self.typeAction.get(comp.childList[0].type, self._cp_unimplemented)(comp.childList[0])

            # loop break action
            if not childIsCharacter:
                self._appendTemplate(T_YIELD)

            # close loop
            self._appendTemplate(T_LOOP_TEST, index, loopHead - len(self.program))
            self._freeCounter()

        #
        # optional repeats
        #

        if comp.repeatMax == VM_COUNT_UNMEASURED:
            count = VM_COUNT_UNMEASURED
        else:
            count  = comp.repeatMax - comp.repeatMin

        # if possible use enumeration or simple loops without new threads
        if (comp.attr & AT_DISJOINT) and childIsCharacter:

            # even if loop size is big, enumerate first
            enumCount    = count
            branchOffset = enumCount - 1
            if count > 64:
                enumCount     = 64
                branchOffset  = 66

            # enumerated tests
            for i in range(enumCount):
                if comp.attr & AT_CONTROLLING:
                    self._appendTemplate(T_CHAR_ANCHOR_BRANCH, branchOffset - i, comp.childList[0].ref)
                else:
                    self._appendTemplate(T_CHAR_BRANCH, branchOffset - i, comp.childList[0].ref)

            # finish using counting loop if needed
            if (count - enumCount) > 1:

                # add counter
                index       = self._getCounter()
                self._appendTemplate(T_LOOP_SET_COUNT, index, count - enumCount)

                loopHead = len(self.program)

                # loop action
                if comp.attr & AT_CONTROLLING:
                    self._appendTemplate(T_CHAR_ANCHOR_BRANCH, 1, comp.childList[0].ref)
                else:
                    self._appendTemplate(T_CHAR_BRANCH, 1, comp.childList[0].ref)

                # loop end
                self._appendTemplate(T_LOOP_TEST, index, loopHead - len(self.program))

                # free counter
                self._appendTemplate(T_LOOP_SET_COUNT, index, 0)
                self._freeCounter()

            # prevent future control optimise in case loop is inner nested loop)
            comp.attr &= ~AT_CONTROLLING
            return

        #
        # remaining optional repeats require multi-threading (not disjoint)
        #

        # get lookahead character if possible
        if hasattr(comp, 'lookAhead') and comp.lookAhead != None:
            lookAhead = self._getPreview(comp.lookAhead)
        else:
            lookAhead = -1

        # no need for loop, just a single action
        if count == 1:

            #lookahead if possible
            if (lookAhead >= 0):
                self._appendTemplate(T_JMP_LOOKAHEAD, 1, lookAhead)
            else:
                self._appendTemplate(T_NULL)

            # postpone new thread that jumps test until we know the terminating thread address
            insertPosn = len(self.program) - 1

            # loop action
            if childIsCharacter and comp.attr & AT_CONTROLLING:
                self._appendTemplate(T_CHAR_ANCHOR, comp.childList[0].ref)
            else:
                self.typeAction.get(comp.childList[0].type, self._cp_unimplemented)(comp.childList[0])

            #finally add the missing optional loop jump
            self.program[insertPosn] = (VM_INSTR_NEW_THREAD, 0, len(self.program) - insertPosn, False)

        # counter driven optional loop
        elif count > 1:

            # add counter
            index       = self._getCounter()
            self._appendTemplate(T_LOOP_SET_COUNT, index, count)

            loopHead = len(self.program)

            #lookahead if possible
            if (lookAhead >= 0):
                self._appendTemplate(T_JMP_LOOKAHEAD, 1, lookAhead)
            else:
                self._appendTemplate(T_NULL)

            # postpone new thread that jumps test until we know the terminating thread address
            insertPosn = len(self.program) - 1

            # loop action
            if childIsCharacter and comp.attr & AT_CONTROLLING:
                self._appendTemplate(T_CHAR_ANCHOR, comp.childList[0].ref)
            else:
                self.typeAction.get(comp.childList[0].type, self._cp_unimplemented)(comp.childList[0])

            # loop break action
            self._appendTemplate(T_YIELD)

            # end loop
            self._appendTemplate(T_LOOP_TEST, index, loopHead - len(self.program))

            #add the missing optional loop jump (now know where the loop end is)
            self.program[insertPosn] = (VM_INSTR_NEW_THREAD, 0, len(self.program) - insertPosn, False)

            # free counter
            self._appendTemplate(T_LOOP_SET_COUNT, index, 0)
            self._freeCounter()

        # no further need for control - remove in case loop is re-entered
        comp.attr &= ~AT_CONTROLLING

    def _cp_action(self, comp):

        # actions without aux characters
        if comp.action & (PROG_BUFF_START | PROG_BUFF_END):
            if comp.action & PROG_BUFF_START:
                self._appendTemplate(T_TEST_START)
            else:
                self._appendTemplate(T_TEST_END)
            return

        if comp.action & PROG_BACKREFERENCE:
            self._appendTemplate(T_PROG_BACKREFERENCE, comp.ref)
            return

        # with aux characters
        charIndex = self.root.auxChars.childIndex

        if comp.action & (PROG_TEXT_START | PROG_TEXT_END):
            # dfacompiler will have folded ^ $ into PROG_BUFF... if not multiline
            # so don't need to consider multiline flag here
            if comp.action & PROG_TEXT_START:
                self._appendTemplate(T_PROG_LINESTART,
                                     charIndex['{=newline}'].ref,
                                     charIndex['{=newline}'].ref)
            else:
                self._appendTemplate(T_PROG_LINEEND,
                                     charIndex['{=newline}'].ref,
                                     charIndex['{=newline}'].ref)

        elif comp.action & (PROG_WBOUNDARY | PROG_NWBOUNDARY):
            if comp.action & PROG_WBOUNDARY:
                self._appendTemplate(T_PROG_WD_BOUND,
                                     charIndex['{=word}'].ref,
                                     charIndex['{=not_word}'].ref,
                                     charIndex['{=not_word}'].ref,
                                     charIndex['{=word}'].ref)
            else:
                self._appendTemplate(T_PROG_NOT_WD_BOUND,
                                     charIndex['{=word}'].ref,
                                     charIndex['{=word}'].ref,
                                     charIndex['{=not_word}'].ref,
                                     charIndex['{=not_word}'].ref)

        elif comp.action & PROG_GRAPHEME:
            nextProg = len(self.program) + 20
            self._appendTemplate(T_JUMP_IF_START, nextProg - len(self.program))
            self._appendTemplate(T_JUMP_IF_END, nextProg - len(self.program))
            self._appendTemplate(T_FAIL_BETWEEN,
                                 charIndex['{grapheme_cluster_break=cr}'].ref,
                                 charIndex['{grapheme_cluster_break=lf}'].ref)
            self._appendTemplate(T_JUMP_IF_AFTER,
                                 charIndex['{grapheme_cluster_break=control_cr_lf}'].ref, nextProg - len(self.program))
            self._appendTemplate(T_JUMP_IF_BEFORE,
                                 charIndex['{grapheme_cluster_break=control_cr_lf}'].ref, nextProg - len(self.program))
            self._appendTemplate(T_FAIL_BETWEEN,
                                 charIndex['{grapheme_cluster_break=l}'].ref,
                                 charIndex['{grapheme_cluster_break=l_v_lv_lvt}'].ref)
            self._appendTemplate(T_FAIL_BETWEEN,
                                 charIndex['{grapheme_cluster_break=lv_v}'].ref,
                                 charIndex['{grapheme_cluster_break=v_t}'].ref)
            self._appendTemplate(T_FAIL_BETWEEN,
                                 charIndex['{grapheme_cluster_break=lvt_t}'].ref,
                                 charIndex['{grapheme_cluster_break=t}'].ref)
            self._appendTemplate(T_FAIL_BETWEEN,
                                 charIndex['{grapheme_cluster_break=regional_indicator}'].ref,
                                 charIndex['{grapheme_cluster_break=regional_indicator}'].ref)
            self._appendTemplate(T_FAIL_BEFORE,
                                 charIndex['{grapheme_cluster_break=extend}'].ref)
            self._appendTemplate(T_FAIL_BEFORE,
                                 charIndex['{grapheme_cluster_break=spacingmark}'].ref)
            self._appendTemplate(T_FAIL_AFTER,
                                 charIndex['{grapheme_cluster_break=prepend}'].ref)
            # need to check if on valid character cut, otherwise previous 'any' may be false
            self._appendTemplate(T_PREVIOUS, charIndex['{=any}'].ref)

    def _cp_unimplemented(self, comp):
        raise SystemError("Unimplemented compiler feature, component type: ".format(comp.type))

    def _appendTemplate(self, template, *subs):
        '''Substitute the provided parameters in the template, then append to program.

        A template has the format [(instruction, index, address, flag),...] the same
        as a thread, but values may be marked 'SUBSTITUTE' to indicate the need to fill
        with relevant params
        '''
        si = 0
        for instr in template:
            # check number to substitute
            count = 0
            for val in instr:
                if val == SUBSTITUTE:
                    count += 1
            if si + count > len(subs):
                raise SystemError("_appendTemplate() not provided with sufficient substitution parameters")
            if count == 0:
                # no subs
                self.program.append(instr)
            else:
                # sub any marked values
                newInstr = []
                for val in instr:
                    if val == SUBSTITUTE:
                        newInstr.append(subs[si])
                        si += 1
                    else:
                        newInstr.append(val)
                self.program.append(tuple(newInstr))
        if si != len(subs):
            raise SystemError("_appendTemplate() - too many substitution parameters")

    def _getCounter(self):
        if self.counter == VM_MAX_COUNTERS:
            msg = "Loop nesting exceeds the maximum depth limit of {:d}.".format(VM_MAX_COUNTERS)
            compileLog.error(msg)
            raise SyntaxError(msg)
        res = self.counter
        self.counter += 1
        return res

    def _freeCounter(self):
        self.counter -= 1

    def _getGroupMarkIndex(self):
        if self.nextGroup >= VM_MAX_MARK_PAIRS:
            msg = "Re is is too complex for the available number of group mark descriptors (as well as user matches they are needed for repeats and other group types."
            compileLog.error(msg)
            raise SyntaxError(msg)
        res = self.nextGroup
        self.nextGroup += 1
        return res

    def _freeGroupMarkIndex(self):
        self.nextGroup -= 1

    def _getPreview(self, comp):
        ''' If possible find a character that is required to
            allow the re to progress.
        '''
        if comp.type == TYPE_COMPILED:
            # character found, protect from using twice
            if comp.attr & AT_USED_AS_LOOKAHEAD:
                return -1
            comp.attr |= AT_USED_AS_LOOKAHEAD
            return comp.ref

        elif comp.type == TYPE_REPEAT:
            if comp.repeatMin > 0:
                # loop spec has a compulsory element
                return self._getPreview(comp.childList[0])
            else:
                # loop has only optional element, must consider lookahead option
                if hasattr(comp, 'previewDFA'):
                    if comp.attr & AT_USED_AS_LOOKAHEAD:
                        return -1
                    comp.attr |= AT_USED_AS_LOOKAHEAD
                    return comp.previewDFA
                else:
                    return -1

        elif comp.type == TYPE_ALT:
            # alt can only return a decision character if preset
            if hasattr(comp, 'previewDFA'):
                comp.attr |= AT_USED_AS_LOOKAHEAD
                return comp.previewDFA

        elif comp.type == TYPE_GROUP:
            if comp.attr & AT_NOTCONSUME:
                return -1
            if hasattr(comp, 'previewDFA'):
                return comp.previewDFA
            return self._getPreview(comp.childList[0])

        # default fail
        return -1

    def _separateControlLoop(self, comp, optFound):
        ''' Test if a required loop needs a separate first pass

        If a required loop contains a nested loop with a controlling repeat
        but further iterations of the nested loop are optional or have interposing
        characters then only the first pass can control the anchor, so the outer
        loop must separate its first required pass from subsequent loops.

        This test is used to tell the outer loop to separate its first pass.

        Assumes it is called on the child of the outer loop with opFound False.
        '''
        if comp.type == TYPE_GROUP:
            if comp.attr & AT_NOTCONSUME:
                return False
            opt = True if len(comp.childList) > 1 else optFound
            return self._separateControlLoop(comp.childList[0], opt)

        elif comp.type == TYPE_REPEAT:
            if comp.attr & AT_CONTROLLING:
                return optFound
            elif comp.repeatMin == 0:
                # further nested loop will not be controlling
                return False
            return self._separateControlLoop(comp.childList[0], optFound)

        else:
            # will not be a controlling loop
            return False

    def _getControllingRepeat(self, comp):
        ''' Return unique controlling repeat if one exists.

            This will not work through alt statements and will
            mark any found repeats as consumed to avoid repeating
            guards in recursive structure.
        '''
        if comp.type == TYPE_GROUP:
            if comp.attr & AT_NOTCONSUME:
                return None
            return self._getControllingRepeat(comp.childList[0])

        elif comp.type == TYPE_REPEAT:
            if comp.attr & AT_CONTROL_CONSUMED:
                return None
            if comp.attr & AT_CONTROLLING:
                comp.attr |= AT_CONTROL_CONSUMED
                return comp
            return self._getControllingRepeat(comp.childList[0])

        else:
            return None

    def _push_bReturn(self, pc):
        self.bReturn.append(pc)

    def _pop_bReturn(self):
        if len(self.bReturn) == 0:
            raise SystemError("Attempt to pop empty b-node tree return address")
        return self.bReturn.pop()

    def _bReturnEmpty(self):
        if len(self.bReturn) == 0:
            return True
        return False


def _numberGroups(root, indexAlts):
    ''' allocate numbers (mark indexes) to groups:
        - allocate early numbers to submatch groups
        - allocate final returned group to altindex if enabled
        - find reverse order of matching to support lastmatched in match object
        - resolve backreference names to group numbers
    '''

    # first assign the groups the user wants to mark to place them in the lowest numbered slots
    # outer group (root) is always added
    nextGroup = 0
    nameMap   = {}
    groupMap  = {}
    for comp in root.filteredBy(TYPE_GROUP):
        if comp.attr & (AT_NOTCAPTURE | AT_NOTCONSUME) and (comp is not root):
            continue
        if hasattr(comp, 'groupName'):
            nameMap[comp.groupName] = nextGroup
        if nextGroup >= VM_MAX_MARK_PAIRS:
            msg = "Too many user-specified match groups to mark; maximum is {:d}".format(VM_MAX_MARK_PAIRS)
            compileLog.error(msg)
            raise ValueError(msg)
        else:
            comp.markIndex = nextGroup
            groupMap[nextGroup] = comp
            nextGroup += 1

    # build group child masks - zero set for index of any group below indexed group
    subMasks = [VM_MARK_MASK] * VM_MAX_MARK_PAIRS
    _markSubgroups(root, subMasks)

    # find the order in which groups will end to allow lastmatched to be found on match
    endOrder = {}    # markIndex -> order
    posn     = 0
    stack    = [0] * nextGroup
    sp       = 0
    for depth, comp in root:
        if comp == root:
            continue
        while sp > 0:
            if depth > stack[sp - 1][1]:
                break
            endOrder[stack[sp - 1][0]] = posn
            sp   -= 1
            posn += 1
        if (not hasattr(comp, 'markIndex')):
            continue
        stack[sp] = (comp.markIndex, depth)
        sp       += 1
    while sp > 0:
        endOrder[stack[sp - 1][0]] = posn
        sp   -= 1
        posn += 1

    if indexAlts:
        if nextGroup >= VM_MAX_MARK_PAIRS:
            msg = "No remaining mark descriptors to allow INDEXALT marks, need to specify at least one less match group; maximum is {:d}".format(VM_MAX_MARK_PAIRS - 1)
            compileLog.error(msg)
            raise ValueError(msg)
        root.altMarkIndex = nextGroup
        nextGroup += 1

    # resolve any names used for backreferences, and mark groups that are referenced
    backrefMask = 0
    for comp in root.filteredBy(TYPE_PROG):
        if comp.action & PROG_BACKREFERENCE:
            # lookup name if needed
            if hasattr(comp, 'name'):
                if comp.name in nameMap:
                    comp.ref = nameMap[comp.name]
                else:
                    raise SystemError("Attempt to compile unrecognised backreference name: {}".format(comp.name))
            backrefMask |= (1 << comp.ref)
            groupMap[comp.ref].attr |= AT_BACKREFERENCED

    return  nextGroup, nameMap, endOrder, backrefMask, subMasks


def _markSubgroups(comp, subMasks):
    ''' recursively build masks which have bits reset for any
        numbered group in the child tree
    '''
    mask = VM_MARK_MASK
    if hasattr(comp, 'childList'):
        for child in comp.childList:
            mask &= _markSubgroups(child, subMasks)

    if comp.type == TYPE_GROUP and hasattr(comp, 'markIndex'):
        mask &= ~(1 << comp.markIndex)
        subMasks[comp.markIndex] = mask

    return mask


def _markStartAttributes(root, comp, belowLoop=False):
    ''' Tests if a tree begins with a construct that needs
    special processing and if so annotates the root node with:
    AT_START_BUFFER_START    Anchor only at the start of the text buffer
    AT_START_LOOP_DOT        Anchor at start, after publish, or after newline

    belowloop is used to show that a loop has been found
    '''

    if comp.type == TYPE_GROUP:
        if comp.attr & AT_NOTCONSUME:
            return
        firstChild = comp.childList[0]
        return _markStartAttributes(root, firstChild, belowLoop=belowLoop)

    elif comp.type == TYPE_REPEAT:
        if belowLoop or comp.repeatMax != VM_COUNT_UNMEASURED:
            return
        return _markStartAttributes(root, comp.childList[0], belowLoop=True)

    elif comp.type == TYPE_COMPILED:
        return

    elif comp.type == TYPE_PROG:
        if (not belowLoop) and (comp.action & PROG_BUFF_START):
            root.attr |= AT_START_BUFFER_START
        elif (not belowLoop) and (comp.action & PROG_TEXT_START):
            root.attr |= AT_START_LOOP_DOT
        return

    else:
        return


def _markControllingRepeats(comp, guardCount):
    ''' This marks a repeat as one which may advance the anchor point

    If a required character repeat which is disjoint with the sequel occurs at
    the start of a re and the re match subsequently fails there is no likelihood
    that moving the anchor before a failed repeat character will result in
    match so the anchor can be stepped to beyond the last character tested.

    If an optional repeat (anywhere) has been attempted and subsequently failed
    then it then the sequel will have been tested in every position in which that
    loop executed and will always fail from these positions.

    Returns number of repeats marked - the guardCount
    Finding a group which is backreferenced terminates the search

    '''
    if (guardCount >= VM_MAX_GUARDS):
        return guardCount, False

    if comp.type == TYPE_COMPILED:
        return guardCount, False

    elif comp.type == TYPE_GROUP:
        if comp.attr & AT_NOTCONSUME:
            return guardCount, False
        if comp.attr & AT_BACKREFERENCED:
            return guardCount, True
        for child in comp.childList:
            guardCount, backref = _markControllingRepeats(child, guardCount)
            if backref:
                return guardCount, True
        return guardCount, False

    elif comp.type == TYPE_ALT:
        backref = False
        for child in comp.childList:
            guardCount, newref = _markControllingRepeats(child, guardCount)
            if newref:
                backref = True
        return guardCount, backref

    elif comp.type == TYPE_REPEAT:
        if comp.childList[0].type == TYPE_COMPILED and (comp.attr & AT_DISJOINT or comp.repeatMin == 0) and (comp.repeatMax > LOOP_THRESHOLD_FOR_GUARDS):
            comp.attr |= AT_CONTROLLING
            comp.guardIndex = guardCount
            guardCount += 1
            return guardCount, False
        elif comp.repeatMin == 0:
            # can only recursive if it is certain the child will execute
            return guardCount, False
        # recursive call with at least one required repeat
        return _markControllingRepeats(comp.childList[0], guardCount)

    else:
        return guardCount, False


def printProgram(prog):
    ''' program print for compiler debugging
    '''
    instruction = {0x0: 'NULL           ',
                   0x1: 'new-thread     ',
                   0x2: 'reset to mark  ',
                   0x3: 'set count      ',
                   0x4: 'publish        ',
                   0x5: 'scan           ',
                   0x6: 'set-context    ',
                   0x7: 'set-mark       ',
                   0xA: 'mark-start     ',
                   0xE: 'mark-end       ',

                   }
    charFlags   = {0x1: 'jump ',
                   0x2: 'prev ',
                   0x4: 'cont ',
                   0x8: 'zero ',
                   0x10: 'ctrl '
                   }

    testFlags   = {0x1: 'not  ',
                   0x2: 'flags',
                   0x4: 'count',
                   0x8: 'guard',
                   0x10: 'back '}

    vmFlags     = {0x1: ' char',
                   0x2: ' start',
                   0x4: ' anchor',
                   0x8: ' end',
                   0x10: ' published'}

    print("******* Compiled Program *******")
    for j, smt in enumerate(prog):
        # convert addresses to absolutes

        index   = smt[1]
        if (smt[0] & VM_INSTR_CHARACTER) and (smt[0] & VM_FLAG_BRANCH):
            index += (j + 1)
        address = smt[2]
        if (smt[0] == VM_INSTR_NEW_THREAD) or (smt[0] & VM_INSTR_TEST):
            address += j

        if smt[0] & VM_INSTR_CHARACTER:
            instr = 'char '
            charFlagCount = 0
            for f in charFlags:
                if f & smt[0]:
                    instr += charFlags[f]
                    charFlagCount += 5
            instr += ' ' * (15 - charFlagCount)
            if (smt[0] & VM_FLAG_BRANCH):
                instr += '{:4x} {:4x}'.format(index, address)
            else:
                instr += '     {:4x}'.format(address)

        elif smt[0] & VM_INSTR_TEST:
            instr = 'test '
            charFlagCount = 0
            for f in testFlags:
                if f & smt[0]:
                    instr += testFlags[f]
                    charFlagCount += 5
            instr += ' ' * (15 - charFlagCount)
            instr += '{:4x} {:4x}'.format(index, address)

            if smt[0] & VM_FLAG_TEST_FLAGS:
                instr += ' ('
                for v in vmFlags:
                    if v & smt[1]:
                        instr += vmFlags[v]
                instr += ')'

        else:
            instr = instruction[smt[0]]
            if smt[0] & 2:
                instr += '     {:4x}'.format(index)
            else:
                instr += '         '
            if smt[0] & 1:
                instr += ' {:4x}'.format(address)
            else:
                instr += '     '
        if smt[3]:
            instr += ' HALT'
        else:
            instr += '     '

        print('{:4x}:\t'.format(j) + instr)
        if smt[3]:
            print('......................')
    print("********************************")
