/* **********************************************************

    Jigsaw Virtual Machine: Core VM
    
    This implements a bytecode NFA VM to implement unicode REs
	
	The character matching within the re is done with a nested 
	state-table driven DFA

    @author: Howard Chivers
    @version: 1.1.3 
    
Copyright (c) 2015, Howard Chivers
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this
  list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.

* Neither the names  jigsaw, jsre, jsvm nor the names of its contributors 
  may be used to endorse or promote products derived from this software 
  without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
    
************************************************************ */

#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include "jsvm.h"

int encodeByteCode(ByteCode * const byteCode,uint8_t ** encodedBytes);


//************************************************************
//  Misc External Functions
//************************************************************

int findByte(uint8_t * const buffer,int start,int stop,uint8_t test) {
    //simple byte searching within buffer
    uint8_t *block = buffer + start;
    uint8_t * found = memchr(block,test,stop-start);
    if (found == NULL) return -1;
    return (int)(found - buffer);
} 

//************************************************************
// Loader functions
//
// used to build the vm and its program
// as far as possible consitency checking done here and not in real time
//
//************************************************************

int allocateMachine(VirtualMachine * tvm) {
    /*
	allocate memory and zero values to a virtual machine
	*/
    
    //default values
    tvm->transition            = NULL;
    tvm->stateLength           = 0;
	tvm->allocatedStates       = 0;
    tvm->program               = NULL;
    tvm->programLength         = 0;
	tvm->allocatedInstructions = 0;
    tvm->startList             = NULL;
    tvm->startLength           = 0;
	tvm->trace				   = 0;
    
    tvm->transition		= (uint16_t *) malloc(256 * INIT_STATE_SIZE * sizeof(uint16_t));
    if (tvm->transition == NULL) return FAILED_TO_ALLOCATE_MEMORY;
	tvm->allocatedStates = INIT_STATE_SIZE;
    
    tvm->program        = (ByteCode *) malloc(INIT_BYTECODE_SIZE  * sizeof(ByteCode));
    if (tvm->program    == NULL) goto AllocateError;
	tvm->allocatedInstructions = INIT_BYTECODE_SIZE;
    
    tvm->startList      = (Start *)malloc(START_LIST_SIZE  * sizeof(Start));
    if (tvm->startList  == NULL) goto AllocateError;
    
    return 0; //OK
    
AllocateError: 
    freeMachine(tvm);
    return FAILED_TO_ALLOCATE_MEMORY;
}   

int freeMachine(VirtualMachine * tvm) {
    if (tvm->transition!=NULL) free(tvm->transition);
    tvm->transition = NULL;
    
    if (tvm->program!=NULL) free(tvm->program);
    tvm->program = NULL;
    
    if (tvm->startList!=NULL) free(tvm->startList);
    tvm->startList = NULL;
    
    return 0;
}

bool checkAllocation(void **heap, int size, uint32_t *allocated, uint32_t *used, uint32_t requested, uint32_t increment, uint32_t maximum) {
	/* checks if data can be accommodated in the space, if not allocates additional heap
	  if within limit & copies over the current content.
	*/
	uint32_t newAllocated;
	void * newHeap;

	// is already allocated?
	if (*used + requested < *allocated) return TRUE;

	// fit within maximum size?
	for (newAllocated = *allocated; newAllocated < (*used + requested) ; newAllocated += increment);
	if (newAllocated > maximum) newAllocated = maximum;
	if (newAllocated < (*used + requested)) return FALSE;

	//allocate
	newHeap		= (void *) malloc(newAllocated * size);
    if (newHeap == NULL) return FALSE;
	
	memcpy(newHeap, *heap, *used * size);
	if (*heap!=NULL) free(*heap);
	*heap = newHeap;
	*allocated = newAllocated;
	return TRUE;
}

int newStates(VirtualMachine * tvm, uint32_t start, uint32_t total) {
    /*
	initialises (ie writes CHARACTER_FAIL) to indexed state
    can only do this once to create a new state, and it must be sequential from the previous highest state
	start = index of first state to be initilaised
	total = resulting number of states (last state + 1)  
	*/
    uint32_t i;

    //basic checks
    if (tvm->transition==NULL) return TVM_NOT_INITIALISED;
    if (tvm->stateLength != start) return INVALID_STATE_REQUESTED;
	if (!checkAllocation((void **) &tvm->transition, 256 * sizeof(uint16_t), &tvm->allocatedStates, &tvm->stateLength, total - start, STATE_SIZE_INC, MAX_STATE_SIZE)) {
		return TOO_MANY_STATES_REQUESTED;
	}

	for (i = start << 8; i < total << 8; i++) {  
		//initialise transition table
		tvm->transition[i] = CHARACTER_FAIL;
	}
	tvm->stateLength = total;
    
    return 0;
}

int newTransitionRange(VirtualMachine * tvm, const uint32_t stateIndex,const uint32_t rangeStart,const uint32_t rangeEnd, const uint16_t transition) {
    /*
	specify a new transtion from indexed state resulting from all givenbytes in the rangeStart,rangeEnd inclusive list 
    transition must be to a valid state or to CHARACTER_OK
	*/

    uint32_t start, end, i;

	start = rangeStart & 0xFF;
	end   = rangeEnd   & 0xFF;

    //basic checks
    if (tvm->transition==NULL) return TVM_NOT_INITIALISED;
    if (tvm->stateLength <= stateIndex) return INVALID_STATE_INDEX_FOR_TRANSITION;

    //check address
    if ((transition != CHARACTER_OK) && (transition>=tvm->stateLength)) return TRANSITION_TO_UNDEFINED_STATE;
    
    //record state transition
    for (i=(stateIndex << 8) + start;i<=(stateIndex << 8) + end;i++) tvm->transition[i] = transition;
    return 0;
}

int newTransition(VirtualMachine * tvm, const uint32_t stateIndex,uint8_t * const buffer,const uint32_t length,const uint16_t transition) {
    /*
	specify a new transtion from indexed state resulting from all givenbytes in the (buffer,length) 
    transition must be to a valid state or to CHARACTER_OK
	*/

    uint32_t i,charIndex;

    //basic checks
    if (tvm->transition==NULL) return TVM_NOT_INITIALISED;
    if (tvm->stateLength <= stateIndex) return INVALID_STATE_INDEX_FOR_TRANSITION;
    
    //record state transition
	for (i=0;i<length;i++) {
		charIndex = buffer[i];
		if ((transition != CHARACTER_OK) && (transition>=tvm->stateLength)) return TRANSITION_TO_UNDEFINED_STATE;
		tvm->transition[stateIndex*256 + charIndex] = transition;
	}
    return 0;
}

int newProgram(VirtualMachine * tvm,ByteCode * const byteCode,const uint32_t length) {
	/*
	add a program at the next program location
	byteCode last flag must be used to signal last record
	*/
	uint32_t i,pc, testLength;
	ByteCode  bc;

	//basic checks
	if (tvm->program==NULL) return TVM_NOT_INITIALISED;

	//check length
	if (!(byteCode[length - 1].instruction & FLAG_FINAL)) return END_PROGRAM_NOT_DETECTED;
	testLength = length + tvm->programLength;

	if (!checkAllocation((void **) &tvm->program, sizeof(ByteCode), &tvm->allocatedInstructions, &tvm->programLength, length, BYTECODE_SIZE_INC, MAX_BYTECODE_SIZE)) {
		return PROGRAM_TOO_BIG;
	}

	//process instructions
	for (i = 0 ; i < length ; i++) {
		bc.instruction = byteCode[i].instruction; 
		bc.index       = byteCode[i].index; 
		bc.address     = byteCode[i].address;

		//check test character instruction
		if (bc.instruction & INSTR_CHARACTER) {
			if (bc.address>=tvm->stateLength) {
                return INVALID_TESTCHARACTER_ADDRESS;
			}
			if ((bc.instruction & FLAG_BRANCH) && (bc.index + i >= length)) {
				return INVALID_CHARACTER_BRANCH;
			}
		}

		else if (bc.instruction & INSTR_TEST) {
			if ((bc.address > testLength) && (bc.address != 0)) {
				return INVALID_JUMP_ADDRESS;
            } 
			if ((bc.instruction & FLAG_TEST_COUNT) && (bc.index >= MAX_COUNTERS)) {
				return INVALID_COUNTER_INDEX;
			}
			if ((bc.instruction & FLAG_TEST_BACK) && (bc.index > MAX_MARKS)) {
				return INVALID_BACK_INDEX;
			}

		//check other instructions
		} else switch(bc.instruction & INSTRUCTION_MASK) {
		case INSTR_SCAN:
			if (bc.address>=tvm->stateLength) return INVALID_SCAN_CHARACTER;
			break;

			case INSTR_NEW_THREAD:			
				if (bc.address > testLength) return INVALID_PROGRAM_COUNTER;
				break;

			case INSTR_SET_COUNT:
				if (bc.index>=MAX_COUNTERS) return INVALID_COUNTER_INDEX;
				break;

			case INSTR_SET_MARK:
			case INSTR_RESET_TO_MARK:
			case INSTR_MARK_START:
			case INSTR_MARK_END:
				if (bc.index >= MAX_MARKS) return INVALID_MARK_INDEX;
				break;
				
			case INSTR_SET_CONTEXT:
				if (bc.index >= MAX_MARKS) return INVALID_MARK_INDEX;
				break;

			case INSTR_PUBLISH:
				break;

			default:
				return INVALID_INSTRUCTION;
		}

		pc                 = tvm->programLength;
		tvm->program[pc]   = bc;
		tvm->programLength = pc + 1;
	}
	return 0;
}

int newStart(VirtualMachine * tvm,const uint32_t startIndex,const Start start) {
    /*
	place new start request in start list, must reference a valid expand record
	*/
	Start * newStart;
    
	//basic checks
    if (tvm->startList==NULL) return TVM_NOT_INITIALISED;
    if (tvm->startLength != startIndex) return INVALID_START_REQUESTED;
    if (start.address >= tvm->programLength) return START_REFERENCES_INVALID_PROGRAM;

	newStart  = &(tvm->startList[tvm->startLength++]);
	*newStart = start;
		
    return 0;
}  

//***************************************************
//	Runtime thread management
//
//  Threads are ThreadState structures and are held as linked
//  lists in either free, or temp lists
//  temp is working and only ever should hold 1
//
//  queue is sorted list of pointers; [-1] is next to run
//***************************************************

void resetThreads(Runtime * rtm) {
	/*
	free all threads in runtime
	*/
	int i;

    // default values
    rtm->free        = NULL;
	rtm->temp		 = NULL;
	rtm->queueLength = 0;
	rtm->published   = 0;
	rtm->sequenceCount = 0;

	// init free list
	rtm->free  =  &(rtm->allocated_init[0]);
	for (i=0;i<INIT_THREADHEAP_SIZE - 1;i++) rtm->allocated_init[i].next = &(rtm->allocated_init[i + 1]);

	rtm->allocated_init[INIT_THREADHEAP_SIZE - 1].next = NULL;

	// free extra heap if present
	if (rtm->allocated_extra != NULL) {
		free(rtm->allocated_extra);
		rtm->allocated_extra = NULL;
	}
}

int allocateRuntime(Runtime * rtm) {
    /*
	allocate runtime machine - malloc is for initial thread state
	*/

    rtm->allocated_init		= (ThreadState *) malloc(INIT_THREADHEAP_SIZE * sizeof(ThreadState));
    if (rtm->allocated_init == NULL) return FAILED_TO_ALLOCATE_RUNTIME;
	rtm->allocated_extra    = NULL;
	rtm->anchorGuard        = NULL;   // allocate when start is known


	resetThreads(rtm);
    return 0; 
}

int freeRuntime(Runtime * rtm) {
	/*
	Free allocated space for runtime
	*/
    if (rtm->allocated_init != NULL) free(rtm->allocated_init);
    rtm->allocated_init = NULL;

	if (rtm->allocated_extra != NULL) free(rtm->allocated_extra);
    rtm->allocated_extra = NULL;

	if (rtm->anchorGuard != NULL) free(rtm->anchorGuard);
	rtm->anchorGuard = NULL;

	return 0;
}

void clearQueue(Runtime * rtm) {
	/*
	free any items remaining in the queue
	*/
	uint32_t i;
	for (i=0; i<rtm->queueLength; i++) {
		rtm->queue[i]->next = rtm->free;
		rtm->free           = rtm->queue[i];
	}
	rtm->queueLength = 0;
}

int allocateToTemp(Runtime * rtm) {
	/*
	allocate from free list to temp
	*/
	int i;

	// already available?
	if (rtm->temp!=NULL) return 0;

	// check if free entries available
	if (rtm->free == NULL) {
		if (rtm->allocated_extra != NULL) return THREAD_HEAP_OVERFLOW;
		
		// extra not allocated, can add space to heap
		rtm->allocated_extra		= (ThreadState *) malloc((MAX_THREADHEAP_SIZE - INIT_THREADHEAP_SIZE) * sizeof(ThreadState));
        if (rtm->allocated_extra == NULL) return FAILED_TO_ALLOCATE_THREAD_HEAP;

		// init free list with new heap
		rtm->free  =  &(rtm->allocated_extra[0]);
		for (i=0;i<(MAX_THREADHEAP_SIZE - INIT_THREADHEAP_SIZE) - 1;i++) rtm->allocated_extra[i].next = &(rtm->allocated_extra[i + 1]);

		rtm->allocated_extra[(MAX_THREADHEAP_SIZE - INIT_THREADHEAP_SIZE) - 1].next = NULL;
	}

	// move head of free to temp
	rtm->temp = rtm->free;
	rtm->free = rtm->temp->next;
	return 0;
}

void freeTemp(Runtime * rtm) {
	/*
	Free the current temp thread
	*/
	if (rtm->temp==NULL) return;
	rtm->temp->next = rtm->free;
	rtm->free       = rtm->temp;
	rtm->temp       = NULL;
}

void enqueueTemp(Runtime * rtm, uint8_t * const buffer) {
	/*
	take thread from temp and place in queue
	the queue is byte ordered, search starts at the tail
	*/
	ThreadState *insertThread, **queue, *testThread;
	uint16_t * p_leftCount, * p_rightCount, testFlag, insertFlag;
	int res, length, lower, middle, upper;
	uint32_t i, j, k, m, testLen, insertLen;
	uint32_t started_test, started_insert, marked_test, marked_insert;
	uint32_t	insert_byteIndex;		
	int32_t		insert_programCounter;

	insertThread          = rtm->temp;
	insert_byteIndex      = insertThread->p.byteIndex;
	insert_programCounter = insertThread->p.programCounter;
	queue                 = rtm->queue;
	length                = rtm->queueLength;
	started_insert		  = insertThread->p.startedMask;
	marked_insert		  = insertThread->p.markedMask;

	//search for insert position
    lower = 0;    
	upper = length - 1;
    while (upper >= lower) {
        middle = ( upper + lower ) / 2;

		// input byte index 
		testThread = queue[middle];
		res = testThread->p.byteIndex - insert_byteIndex;
		if (res) goto continueSearch; 

		// program state
		res = testThread->p.programCounter - insert_programCounter;
		if (res) goto continueSearch;

		// counters
		p_leftCount  = testThread->p.counter;
		p_rightCount = insertThread->p.counter;
		for (i=0;i<MAX_COUNTERS;i++) { 
			res = *(p_rightCount++) - *(p_leftCount++);  // largest counter is earliest
			if (res) goto continueSearch;
		}

		started_test   = testThread->p.startedMask;
		marked_test    = testThread->p.markedMask;
		
		// backreferences keep apart possible solutions - order is arbitrary
		if (rtm->backrefMask) {

			j = marked_test & rtm->backrefMask;
			k = started_test & rtm->backrefMask;

			// state different, keep apart
			res = k - (started_insert & rtm->backrefMask);
			if (res)  goto continueSearch;
			res = j - (marked_insert & rtm->backrefMask);
			if (res)  goto continueSearch;

			i = 0;
			while(j | k) {
				if (k & 1) {
					// check length of started threads - if starts the same content is the same
					res = testThread->groupMark[i].start - insertThread->groupMark[i].start;
					if (res) goto continueSearch;
				}
				if (j & 1) {
					// check length of marked groups
					res =  insertThread->groupMark[i].end - insertThread->groupMark[i].start - testThread->groupMark[i].end + testThread->groupMark[i].start;
					if (res) goto continueSearch;

					// check content of marked groups
					insertLen = insertThread->groupMark[i].start;
					testLen   = testThread->groupMark[i].start;
					m = insertThread->groupMark[i].end;
					while (insertLen <= m) {
						res = (int) buffer[insertLen++] - (int) buffer[testLen++];
						if (res) goto continueSearch;
					}
				}
				j >>= 1;
				k >>= 1;
				i++;	
			}
		}

		// here if exact match - this is a thread collision
		// First give priority to short groups if any marked
		res = 0;
		if (insertThread->p.context) {
			k = (started_test | started_insert | marked_test | marked_insert) & insertThread->p.context;
			i   = 0;
			j   = 1;
			while(k) {
				if (k & 1) {
					if (!((started_test | marked_test) & j)) {
						res = 1;
						break;
					}
					if (!((started_insert | marked_insert) & j)) {
						res = -1;
						break;
					}
					if (started_insert & j) {
						res = insert_byteIndex - 1 - insertThread->groupMark[i].start;
					} else {
						res = insertThread->groupMark[i].end - insertThread->groupMark[i].start;
					}
					if (started_test & j) {
						res -= (testThread->p.byteIndex - 1 - testThread->groupMark[i].start);
					} else {
						res -= (testThread->groupMark[i].end - testThread->groupMark[i].start);
					}
					if (res) break;
				}
				k >>= 1;
				i += 1;
				j <<= 1;
			}
			// if res > 0  insert is longer than test
			if (res > 0) goto freeInsertThread;
			if (res < 0) goto freeTestThread;
		}

		// check thread preference using group encountered sequence
		// start priority, then length priority, order only matters, not group ID
		if (!insertThread->p.sequenceCount) goto freeInsertThread;
		if (!testThread->p.sequenceCount) goto freeTestThread;

		i = 0;
		j = 0;
		while ((i < insertThread->p.sequenceCount) && (j < testThread->p.sequenceCount)) {
			res = (int) testThread->groupSequence[j].posn - (int) insertThread->groupSequence[i].posn;
			if (res) break;
			testFlag = testThread->groupSequence[j].flag;
			insertFlag = insertThread->groupSequence[i].flag;

			if (((testFlag ^ insertFlag) & OPEN_GROUP_FLAG) && ((testFlag & GROUP_INDEX_MASK) == (insertFlag & GROUP_INDEX_MASK))) {
				// one started other closed of same group
				if (testFlag & OPEN_GROUP_FLAG) goto freeInsertThread;
				else				            goto freeTestThread;
			}
			insertLen = insertThread->groupSequence[j].len;
			while (((i + 1) < insertThread->p.sequenceCount) && ((insertFlag & GROUP_INDEX_MASK) == insertThread->groupSequence[i+1].flag)) {
				i++;
				insertLen += insertThread->groupSequence[i].len;
			}
			testLen = testThread->groupSequence[j].len;
			while (((j + 1) < testThread->p.sequenceCount) && ((testFlag & GROUP_INDEX_MASK) == testThread->groupSequence[j+1].flag)) {
				j++;
				testLen += testThread->groupSequence[j].len;
			}
			if (!((testFlag | insertFlag) & OPEN_GROUP_FLAG)) {
				res = insertLen - testLen;
				if (res) break;
			}
			i++;
			j++;
		}

		// if no bias, select most compact then longest sequence
		if (!res) res = j - i;
		if (!res) res = insertThread->p.sequenceCount - testThread->p.sequenceCount;
		if (res > 0) goto freeTestThread;

freeInsertThread:
		rtm->temp->next = rtm->free;
		rtm->free       = rtm->temp;
		rtm->temp       = NULL;
		return;

freeTestThread:
		testThread->next = rtm->free;
		rtm->free       = testThread;
		queue[middle]   = rtm->temp;
		rtm->temp       = NULL;
		return;
		
continueSearch:
		if (res > 0) {
			lower = middle + 1;
		} else {
			upper = middle - 1;
		}
    }
	memmove(rtm->queue + lower + 1, rtm->queue + lower, (length-lower)*sizeof(ThreadState *));
	rtm->queue[lower] = insertThread;
	rtm->queueLength++;
	rtm->temp = NULL;
	return;
}

int getNextFromQueue(Runtime * rtm) {
	/*
	Get the next Thread from queue to temp, -1 if empty
	*/

	if (rtm->queueLength==0) return -1;  //nothing to move

	//free temp if present
	if (rtm->temp != NULL) {
		rtm->temp->next = rtm->free;
		rtm->free       = rtm->temp;
	}
	
	// move queue tail to temp
	rtm->temp  = rtm->queue[rtm->queueLength - 1];
	rtm->queueLength--;

	return 0;
}

//************************************************************
//  Virtual Machine
//
//  uses three main structures 
//	- the VirtualMachine, which includes the program
//  - the RunTime which holds runtime state
//	- thread structures that hold the state of the current or queued execution
//  
//************************************************************

int setTrace(VirtualMachine * tvm, uint32_t type) {
	/*
	switch on state tracing for debugging 
	*/
	tvm->trace = type;
	return 0;
}

int initRunTime(VirtualMachine * const tvm, Runtime * rtm, const uint32_t start) {
	/*
	initialise the runtime to run a particular re (ie start)
	called externally with start=0 to initialise match
	also used to move between re's

	The actual re is controlled by start, stop, end, stride.

	- start is set to the buffer start + offset 
	- stride is as given
	- stop is the last anchor point + 1
	- end is the last buffer read point + 1

	Sector processing is intended for byte patterns.

	*/
	Start * startSpec;
	uint32_t i;

	if (tvm->trace & TRACE_VERBOSE) printf("Initialse New RE: %4x\n",start);
	rtm->startIndex = start;
	startSpec       = &(tvm->startList[start]);
	
	rtm->anchor     = rtm->bufferSpec.start;
	if (startSpec->command & SECTOR) {
		rtm->anchor += startSpec->offset;
	} 

	rtm->command         = startSpec->command;
	rtm->stop            = rtm->bufferSpec.stop;
	rtm->end             = rtm->bufferSpec.end;
	rtm->endianMask      = startSpec->command & ENDIAN_MASK;
	rtm->backrefMask	 = startSpec->backrefMask;
	rtm->sequenceCount   = 0;
	memcpy(rtm->subgroupMasks, startSpec->subgroupMasks, MAX_MARKS * sizeof(uint32_t));

	rtm->startAnchor     = rtm->anchor;
	rtm->previousByte    = INVALID_BYTE_ADDRESS;
	rtm->returnPairCount = startSpec->returnPairCount;

	// if command is FIXED_ANCHOR ony allow a match from the buffer start
	if (startSpec->command & FIXED_ANCHOR) {
		rtm->stop = 1;
	}

	// if stride is set it overrides default of 1
	if (startSpec->stride != 0) {
		rtm->stride = startSpec->stride;
	} else {
		rtm->stride = 1;
	}

	// init anchorGuard
	if (rtm->anchorGuard!=NULL) free(rtm->anchorGuard);
	rtm->anchorGuard = NULL;
	rtm->guardCount  = startSpec->guardCount;
	if (startSpec->guardCount > 0) {
		rtm->anchorGuard = (AnchorGuard *) malloc(startSpec->guardCount * sizeof(AnchorGuard));
		if (rtm->anchorGuard == NULL) return FAILED_TO_ALLOCATE_RUNTIME;
		for (i = 0; i < startSpec->guardCount; i++) {
			rtm->anchorGuard[i].new_end         = INVALID_BYTE_ADDRESS;
			rtm->anchorGuard[i].constrained_end = INVALID_BYTE_ADDRESS;
		}
	}

	return 0;
}

void initAnchorThread(VirtualMachine * const tvm, Runtime * rtm) {
	/* 
	build a new anchor thread
	*/
	ThreadState * temp;

	//allocate working thread if necessary
	if (rtm->temp==NULL) allocateToTemp(rtm);

	//reset thread
	temp = rtm->temp;
	temp->p.context        = 0;
	temp->p.programCounter = (tvm->startList)[rtm->startIndex].address;
	temp->p.byteIndex      = rtm->anchor;
	temp->p.previousByte   = rtm->previousByte;
	temp->p.highwaterGroup = 0;
	temp->p.sequenceCount  = 0;
	temp->p.startedMask    = 0;
	temp->p.markedMask     = 0;
	temp->p.flags          = VMFL_ANCHOR;
	if (rtm->anchor == rtm->startAnchor) {
		temp->p.flags |= VMFL_START;
	}
	if (rtm->anchor >= rtm->end) {
		temp->p.flags |= VMFL_END;
	}
}

int setNextAnchor(VirtualMachine * const tvm, Runtime * rtm) {
	/*
	simple anchor increments done in locals, this deals with
	published or end of buffer cases

	move to next anchor point, after publish or buffer end 
	returns TRUE (OK) or FALSE (no more work)
	*/
	uint32_t i;

	if (rtm->startIndex >= tvm->startLength) return FALSE; 

	// ensure published results do not overlap
	if (rtm->published) {
		if (((!(rtm->command & SECTOR))) && ((rtm->groupMark[0].end + 1) > rtm->groupMark[0].start)) {
			// normal publish if not a zero width match
			rtm->anchor = rtm->groupMark[0].end + 1;
		} else {
			// sector mode or zero width publish
			rtm->previousByte = INVALID_BYTE_ADDRESS;
		}
		// reset guards after publish
		for (i = 0; i < rtm->guardCount; i++) {
			rtm->anchorGuard[i].new_end         = INVALID_BYTE_ADDRESS;
			rtm->anchorGuard[i].constrained_end = INVALID_BYTE_ADDRESS;
		}
		if (rtm->anchor<rtm->stop) return TRUE;
	}

	//need a new re
	rtm->startIndex += 1;
	if (rtm->startIndex >= tvm->startLength) return FALSE;

	//initialise new re
	initRunTime(tvm,rtm,rtm->startIndex);
	initAnchorThread(tvm,rtm);
	return TRUE;
}

int testPreviousCharacter(VirtualMachine * const tvm,uint8_t * const buffer, Runtime * rtm, int32_t address, uint32_t bytePos, uint32_t * p_thread_previousByte) {
	/*
	!!!it seems that the only way to test many of the new anchor points is to try several byte positions.
	this will test a previous byte if valid, otherwise will try up to 5 previous byte start positions to test for a match
	note that it moves in stride amounts for normal strides
	*/
	uint32_t consumed, rtm_endianMask;
	uint32_t testPos, stride;
	uint32_t thread_previousByte;
	uint32_t state;

	thread_previousByte = *p_thread_previousByte;
	rtm_endianMask  = rtm->endianMask;

	//if previous byte is OK
	if (thread_previousByte!=INVALID_BYTE_ADDRESS) {
		state    = address;
		consumed = 0;
		while(TRUE) {
			//end of buffer?
			if (thread_previousByte + (rtm_endianMask & consumed) >= rtm->end) return 0;

			//run FSM
			state = tvm->transition[(((int) (state) << 8) | ((int) buffer[thread_previousByte+(rtm_endianMask ^ consumed)]))];

			//end?
			if (state == CHARACTER_FAIL) return 0; 
			consumed += 1;
			if (state == CHARACTER_OK) break;
		}
		//detect character size mismatch
		if (thread_previousByte + consumed != bytePos) return 0;
		return consumed;
	}

	// search start position
	testPos = bytePos;

	// use input stride as anchor step for normal encodings
	if (rtm->command & SECTOR) { 
		stride = 1;
	} else {
		stride  = rtm->stride;
	}

	// iterate test positions, limit to 5 byte lookbehind
	while (TRUE) {

		//back to next test position
		testPos -= stride;

		//limit check to 5 bytes
		if ((testPos < rtm->startAnchor) || (testPos + LOOKBEHIND_LIMIT < bytePos )) return 0;

		state    = address;
		consumed = 0;
		while(TRUE) {
			//end of buffer?
			if (testPos + (rtm_endianMask ^ consumed) >= rtm->end) {
				consumed = 0;
				break;
			}

			//run FSM
			state = tvm->transition[(((int) (state) << 8) | ((int) buffer[testPos + (rtm_endianMask ^ consumed)]))];
			if (state == CHARACTER_FAIL) {
				consumed = 0;
				break;
			} 
			consumed += 1;
			if (state == CHARACTER_OK) break;
		}
		if (bytePos == testPos + consumed) {
			//success
			*p_thread_previousByte = testPos;
			return consumed;
		}
	}
	return 0;
}


int findNextMatch(VirtualMachine * const tvm, Runtime * rtm, uint8_t * const buffer) {
    /*
	main re search entry point, takes buffer and the vm + the real time execution structure
    returns next match in rtm match object
	To signal start use initRunTime() before calling 
	
	Note:
	buffer start/stop/end are exclusive (+1) of final bytes, as in python
	match values are inclusive of the full byte range
	see header for start options
    */

	// temp local thread copies
	ThreadState * thread;
	uint32_t	thread_byteIndex;		
	int32_t		thread_programCounter;
	uint16_t	thread_flags;				
	uint32_t	thread_previousByte;

	// temp local rtm copies
	uint32_t	rtm_stride;			// anchor increment
	uint32_t    rtm_endianMask;		// endian mask (orders byte tests)
	uint32_t	rtm_stop;			// limit in buffer of anchor (inclusive address)
	uint32_t	rtm_end;			// end of buffer (inclusive address)
	uint32_t	rtm_anchor;		    // start of re

	// other locals
	ByteCode * tvm_program;
	ByteCode code;
	uint8_t instruction;
	uint16_t * tvm_transition, index;
	int32_t bytesUsed, byteKey, programStart, res;
	uint32_t i, j, k, tst, threadLen, rtmLen, tvm_trace;
	AnchorGuard * anchor;

	// initialise rtm
	if (rtm->startIndex >= tvm->startLength) {
		//anchor ran out on last exit
		rtm->published = 0;
		return 0; 
	}
	clearQueue(rtm);

	// rtm to locals
	rtm_stride				= rtm->stride;
	rtm_endianMask			= rtm->endianMask;
	rtm_stop				= rtm->stop;
	rtm_end					= rtm->end;
	rtm_anchor				= rtm->anchor;
	
	initAnchorThread(tvm, rtm);

	// new start thread to locals
	thread					= rtm->temp;
	thread_byteIndex		= thread->p.byteIndex;
	thread_programCounter	= thread->p.programCounter;
	thread_flags			= thread->p.flags;
	thread_previousByte		= thread->p.previousByte;
	programStart			= thread_programCounter; 

	if (rtm->published) {
		thread_flags      |= VMFL_PUBLISHED;
		rtm->published     = 0;
		rtm->sequenceCount = 0;
	}

	// other locals
	tvm_program				= tvm->program;
	tvm_trace				= tvm->trace;
	tvm_transition			= tvm->transition;

	// scan all anchors for start of RE
	while(TRUE) {

		// run all threads to completion
		while(TRUE) {

			// mark new thread in trace
			if (tvm_trace & TRACE_VERBOSE) printf("->");
nextInstruction:
			// run program to completion
			do {
				code = tvm_program[thread_programCounter++];
				instruction = code.instruction;
				// trace if required
				if (tvm_trace) {
					if (tvm_trace & TRACE_VERBOSE) {
						printf("\tbyte: %4x (%2x)\tpc: %4x = ",thread_byteIndex, buffer[thread_byteIndex], thread_programCounter - 1);
						printf("%4x\t%4x\t%4x\t(%1x)\t",instruction,code.index,code.address,thread_flags);
						tst = instruction  & INSTRUCTION_MASK;
						if (tst & INSTR_TEST) { 
							if (instruction & FLAG_TEST_COUNT) {
									printf("test (%4x)\n", thread->p.counter[code.index]);
								} else {
									printf("test\n");
								}
						} else if (tst & INSTR_CHARACTER)   printf("character\n");
						else switch(tst) {
							case INSTR_NEW_THREAD:    printf("new thread\n");    break;
							case INSTR_RESET_TO_MARK: printf("reset to mark\n"); break;
							case INSTR_SET_COUNT:     printf("set count\n");     break;
							case INSTR_PUBLISH:       printf("publish\n");       break;
							case INSTR_SCAN:          printf("scan\n");          break;
							case INSTR_SET_CONTEXT:   printf("set context\n");   break;
							case INSTR_SET_MARK:      printf("set mark\n");      break;
							case INSTR_MARK_START:    printf("mark start\n");    break;
							case INSTR_MARK_END:      printf("mark end\n");      break;
							default:                  printf("ERROR\n");
						}
					} else {
						printf("%4x\n",thread_programCounter - 1);
					}
				}

				// test characters 
				if (instruction & INSTR_CHARACTER) {
					bytesUsed = 0;
					if (instruction & FLAG_PREVIOUS) {
						// test from previous character byte position
						// no previous position, fails automatically
						if (!(thread_flags & VMFL_START)) {
							// test previous character
							bytesUsed = testPreviousCharacter(tvm,buffer, rtm, code.address, thread_byteIndex, &thread_previousByte);
							if (bytesUsed) {
								thread_flags = thread_flags | VMFL_CHARACTER_OK;
								goto characterOK;
							}
						}
					} else {
						// Run DFA to test character, returns number of bytes used or 0 if failed, sets flag at end of buffer
						tst       = code.address;
						if (!((thread_flags & VMFL_END) || (thread_byteIndex + rtm_endianMask >= rtm_end))) while(TRUE) {

							// run FSM
							tst = tvm_transition[(((int) (tst) << 8) | ((int) buffer[thread_byteIndex + (rtm_endianMask ^ bytesUsed)]))];
							if (tst == CHARACTER_FAIL) break;
							bytesUsed += 1;

							// end of buffer?
							if (thread_byteIndex + (rtm_endianMask ^ bytesUsed) >= rtm_end) {
								if (tst != CHARACTER_OK) break;
								if (!(instruction & FLAG_ZERO_WIDTH)) thread_flags = VMFL_END; 
							}
							if (tst == CHARACTER_OK) {
								thread_flags = thread_flags | VMFL_CHARACTER_OK;
								goto characterOK;
							}
						}
					}
					// loop exit on character failure

					thread_flags = thread_flags & ~VMFL_CHARACTER_OK;
					if (instruction & FLAG_SET_GUARD) {
						anchor = &rtm->anchorGuard[thread->p.guardIndex];

						// this keeps only one range per guarded loop
						// expand range if overlap or keep highest range

						if (anchor->new_end == INVALID_BYTE_ADDRESS) {
							anchor->new_start = thread->p.guardStart;
							anchor->new_end   = thread_byteIndex;
						} else if (!((int) thread_byteIndex < (int) anchor->new_start)) {
							if ((int) thread->p.guardStart > (int) anchor->new_end + 1) {
								anchor->new_start = thread->p.guardStart;
								anchor->new_end   = thread_byteIndex;
							} else {
								if ((int) thread->p.guardStart < (int) anchor->new_start) anchor->new_start = thread->p.guardStart;
								if ((int) thread_byteIndex > (int) anchor->new_end)       anchor->new_end   = thread_byteIndex;
							}
						}
					}
					if (instruction & FLAG_BRANCH) {
						// branch on failure
						thread_programCounter += code.index;
						goto nextInstruction;
					}
					if (!(instruction & FLAG_CONTINUE)) goto programEnd; //character fail exit

					// move to next position
characterOK:		if ((bytesUsed) && !(instruction & (FLAG_PREVIOUS | FLAG_ZERO_WIDTH))) {
						thread_previousByte  =  thread_byteIndex;
						thread_byteIndex     += bytesUsed;
						thread_flags = thread_flags & ~(VMFL_START | VMFL_ANCHOR | VMFL_PUBLISHED);
					}

				} else if (instruction & INSTR_TEST) {

					// default (no flags set) is unconditional jump, NOP if NOT set
					// quick escape if halt
					if (instruction == (INSTR_TEST | FLAG_TEST_NOT | FLAG_FINAL)) break;

					tst = TRUE; 

					// anchor guard test
					if (instruction & FLAG_TEST_GUARD) {
						thread->p.guardIndex = code.index;
						thread->p.guardStart = thread_byteIndex;
						if ((rtm->anchorGuard[code.index].constrained_end != INVALID_BYTE_ADDRESS) && (thread_byteIndex >= rtm->anchorGuard[code.index].constrained_start) && (thread_byteIndex <= rtm->anchorGuard[code.index].constrained_end)) tst = FALSE;

					// counter test
					} else if (instruction & FLAG_TEST_COUNT) {
						//decrement counter and test
						if (thread->p.counter[code.index] == COUNT_UNMEASURED) {
							tst = FALSE;  // count is unmeasured
						} else {
							tst = !(--(thread->p.counter[code.index]));
						}
						// loop done if not progressing
						if (thread->p.loopProtect[code.index] == thread_byteIndex) {
							// loop did not advance the byte position, match must fail
							tst = TRUE;
						} else {
							thread->p.loopProtect[code.index] = thread_byteIndex;
						}

					// VM flag mask test
					} else if (instruction & FLAG_TEST_FLAGS) {
						if ((code.index & VMFL_END) && ((thread_byteIndex + rtm_endianMask) >= rtm_end)) {
							// if at end of buffer, ensure flag set
							thread_flags |= VMFL_END;
							tst = VMFL_END;
						}
						// otherwise just check flags
						tst = (code.index & thread_flags);
					
					// backreference test
					} else if (instruction & FLAG_TEST_BACK) {
						// fail if reference invalid
						tst = (1 << code.index) & thread->p.markedMask;
						i = thread->groupMark[code.index].start;
						k = thread->groupMark[code.index].end + 1;
						if ((tst) && (k > i)) {

							// something to test
							bytesUsed = 0;
							tst = FALSE;
							if (thread_byteIndex < rtm_end) while(!(thread_flags & VMFL_END)) {

								// test next byte (tst FALSE = OK here_
								tst  = buffer[i++] ^ buffer[thread_byteIndex + bytesUsed++];
								if (tst) {
									// match failed
									tst = FALSE;
									break;
								}

								// end of buffer?
								if ((thread_byteIndex + bytesUsed) >= rtm_end) {
									thread_flags = VMFL_END; 
								}

								if (i >= k) {
									// all done, OK
									tst = TRUE;
									thread_previousByte = INVALID_BYTE_ADDRESS;
									thread_byteIndex += bytesUsed;
									thread_flags = (thread_flags & VMFL_END) | VMFL_CHARACTER_OK;
									break;
								}
							}
						}
					}

					if (tst) {
						if (instruction & FLAG_TEST_NOT) {
							// test true and logic inverted
							continue;
						}
					} else {
						if (!(instruction & FLAG_TEST_NOT)) {
							// test false, normal logic
							continue;
						}
					}

					// branch to new prog address if test succeeds
					thread_programCounter = code.address;
					// bypass FINAL instruction check - not relevant
					goto nextInstruction;

				} else switch(instruction & INSTRUCTION_MASK) {

					// all other instructions.

					case INSTR_NEW_THREAD:

						// quick test for does this go to queue head?
						tst = ( !(rtm->queueLength) || (thread->p.byteIndex > rtm->queue[0]->p.byteIndex) );

						if ((instruction & FLAG_FINAL) && tst) {
							// this is yield to self, keep running
							thread_programCounter = code.address;
							goto nextInstruction;
						}

						// restore locals to thread
						thread->p.byteIndex      = thread_byteIndex;
						thread->p.flags          = thread_flags;
						thread->p.previousByte   = thread_previousByte;
						thread->p.programCounter = code.address;

						// queue current thread
						if (tst) {
							// current thread would be at head of queue
							memmove(rtm->queue + 1, rtm->queue, rtm->queueLength*sizeof(ThreadState *));
							rtm->queue[0] = thread;
							rtm->queueLength++;
							rtm->temp = NULL;
						} else {
							enqueueTemp(rtm, buffer);
						}
	
						// exit if just a yield
						if (instruction & FLAG_FINAL) {
							thread = NULL;
							break;
						}

						// otherwise clone thread back to temp to continue
						tst = allocateToTemp(rtm);
                        if (tst) return tst;
						rtm->temp->p = thread->p;
						for (index=0; index < thread->p.highwaterGroup + 1; index++) rtm->temp->groupMark[index]     =  thread->groupMark[index];
						for (index=0; index < thread->p.sequenceCount; index++)      rtm->temp->groupSequence[index] = thread->groupSequence[index];
						thread = rtm->temp;			// point local thread to current working thread
						break;

					case INSTR_RESET_TO_MARK:
						// reset steps out of a group to the left, reset position and sequence
						thread->p.startedMask &= rtm->subgroupMasks[code.index];						
						thread_byteIndex = thread->groupMark[code.index].start;
						if (thread->p.context & (1 << code.index)) break;
						thread->p.sequenceCount = thread->groupMark[code.index].index;
						if (thread->p.sequenceCount == INVALID_START_INDEX) thread->p.sequenceCount = MAX_SEQUENCE;
						break;

					case INSTR_SET_CONTEXT:
						tst = 1 << code.index;
						// set context bit
						thread->p.context |= tst;
						goto markStart;

					case INSTR_PUBLISH:
						// check if is better or worse than previously published result

						// First give test priority to short groups if any marked
						res = 0;
						k = (thread->p.markedMask | rtm->published) & thread->p.context;
						i   = 0;
						j   = 1;
						while(k) {
							if (k & 1) {
								if (!(rtm->published & j)) goto publishYes;
								if (!((thread->p.startedMask | thread->p.markedMask) & j)) goto publishNo;
								
								res = thread->groupMark[i].end - thread->groupMark[i].start - rtm->groupMark[i].end + rtm->groupMark[i].start;
								if (res > 0) goto publishNo;
								if (res < 0) goto publishYes;
							}
							k >>= 1;
							i += 1;
							j <<= 1;
						}

						// check thread preference using group encountered sequence
						// start priority, then length priority, order only matters, not group ID

						if (!thread->p.sequenceCount) goto publishNo;
						if (!rtm->sequenceCount) goto publishYes;

						i = 0;
						j = 0;
						while ((i < thread->p.sequenceCount) && (j < rtm->sequenceCount)) {
							res = rtm->groupSequence[j].posn - thread->groupSequence[i].posn;
							if (res) break;

							threadLen = thread->groupSequence[j].len;
							while (((i + 1) < thread->p.sequenceCount) && ((thread->groupSequence[i].flag & GROUP_INDEX_MASK) == thread->groupSequence[i+1].flag)) {
								i++;
								threadLen += thread->groupSequence[i].len;
							}
							rtmLen = rtm->groupSequence[j].len;
							while (((j + 1) < rtm->sequenceCount) && ((rtm->groupSequence[j].flag & GROUP_INDEX_MASK) == rtm->groupSequence[j+1].flag)) {
								j++;
								rtmLen += rtm->groupSequence[j].len;
							}

							res = threadLen - rtmLen;
							if (res) break;
						i++;
						j++;
						}
						
						// if no bias, select most compact then longest sequence
						if (!res) res = j - i;
						if (!res) res = thread->p.sequenceCount - rtm->sequenceCount;
				
						if (res > 0) goto publishYes;

publishNo:				break;

publishYes:				tst = thread->p.markedMask;
						memcpy(rtm->groupMark, thread->groupMark, sizeof(GroupMarks) * (thread->p.highwaterGroup + 1));
						memcpy(rtm->groupSequence, thread->groupSequence, sizeof(GroupSeq) * thread->p.sequenceCount);
						rtm->sequenceCount = thread->p.sequenceCount;
						rtm->published     = thread->p.markedMask;
						rtm->previousByte  = thread_previousByte;
						rtm->pubReIndex    = rtm->startIndex;
						break;

					case INSTR_SCAN:
						thread_previousByte   = INVALID_BYTE_ADDRESS;
						if ((thread_flags & VMFL_END) || (thread_byteIndex + rtm_endianMask >= rtm_end)) goto programEnd;
						do {
							tst       = code.address;
                            byteKey   = 0;
							while(TRUE) {
								//run FSM
								tst = tvm_transition[(((int) (tst) << 8) | ((int) buffer[thread_byteIndex + (rtm_endianMask ^ byteKey)]))];
								if (tst == CHARACTER_FAIL) break;
								byteKey += 1;

								//end of buffer?
								if ((thread_byteIndex + (rtm_endianMask ^ byteKey) >= rtm_end) && (tst != CHARACTER_OK)) break;

								if (tst == CHARACTER_OK) {
									goto scanOK;
								}
							}
							thread_byteIndex += rtm_stride;
						} while (thread_byteIndex < rtm_stop);
						rtm_anchor       = thread_byteIndex;
						goto programEnd;

						// mark start
scanOK:					rtm_anchor            = thread_byteIndex;
						thread_flags          = thread_flags | VMFL_CHARACTER_OK;
						if (rtm_anchor != rtm->anchor) thread_flags = thread_flags & (!(VMFL_START | VMFL_ANCHOR));
						if ((rtm_anchor + rtm_endianMask) >= rtm_end) thread_flags |= VMFL_END;
						// no break, mark start
						code.index = 0;
				
					case INSTR_MARK_START:
markStart:				thread->groupMark[code.index].start = thread_byteIndex;
						i = rtm->subgroupMasks[code.index];
						j = (1 << code.index);
						thread->p.markedMask &= i;
						thread->p.startedMask = (thread->p.startedMask & i) | j;
						if (code.index > thread->p.highwaterGroup) thread->p.highwaterGroup = code.index;
						if (thread->p.context & j) break;

						// add sequence record for normal (longest) groups
						index = thread->p.sequenceCount++;
						if (index < MAX_SEQUENCE) {
							thread->groupSequence[index].flag   = code.index + OPEN_GROUP_FLAG;
							thread->groupSequence[index].posn   = thread_byteIndex;
							thread->groupMark[code.index].index = index;
						} else {
							thread->p.sequenceCount             = MAX_SEQUENCE;   // restore from ++
							thread->groupMark[code.index].index = INVALID_START_INDEX;
						}
						break;

					case INSTR_MARK_END:
						thread->groupMark[code.index].end = thread_byteIndex - 1;
						j = (1 << code.index);
						thread->p.markedMask   |= j;
						thread->p.startedMask  &= ~j;
						if (thread->p.context & j) break;

						// update sequence record for normal (long) groups
						index = thread->groupMark[code.index].index;
						if (index == INVALID_START_INDEX) break;
						thread->groupSequence[index].len  = thread_byteIndex - thread->groupSequence[index].posn;
						thread->groupSequence[index].flag = code.index;
						break;

					case INSTR_SET_COUNT:
						thread->p.counter[code.index]     = code.address;
						thread->p.loopProtect[code.index] = thread_byteIndex;          
						break;

					case INSTR_SET_MARK:
						thread->groupMark[code.index].end = code.address;
						thread->p.markedMask |= (1 << code.index);
						if (code.index > thread->p.highwaterGroup) thread->p.highwaterGroup = code.index;
						break;

					default:
						return INVALID_INSTUCTION_CODE;
				}
			} while (!(instruction & FLAG_FINAL));

programEnd:	if (rtm->queueLength == 0) break;

			//free temp if present
			if (thread != NULL) {
				thread->next = rtm->free;
				rtm->free    = thread;
			}
	
			// move queue tail to temp
			rtm->temp  = rtm->queue[rtm->queueLength - 1];
			rtm->queueLength--;

			// restore locals from new thread
			thread                = rtm->temp;
			thread_byteIndex      = thread->p.byteIndex;
			thread_programCounter = thread->p.programCounter;
			thread_flags          = thread->p.flags;
			thread_previousByte   = thread->p.previousByte;
		}
		if (tvm_trace & TRACE_VERBOSE) printf("-----------------------\n");  // = end of all traces, need new anchor

		// normal local anchor increment
		rtm_anchor += rtm_stride;

		// prepare restart from next anchor (including before a match so that next call is ready)
		if ( (rtm->published) || (rtm_anchor >= rtm_stop) || (rtm->command & NOINC_ANCHOR)) {
			// long process if published, end of buffer, or special anchor movement
			rtm->anchor = rtm_anchor;
			if (!setNextAnchor(tvm,rtm)) return 0;

			//return if published
			if (rtm->published) {
				return 0;
			}

			//rtm to locals
			rtm_stride				= rtm->stride;
			rtm_endianMask			= rtm->endianMask;
			rtm_stop				= rtm->stop;
			rtm_end					= rtm->end;
			rtm_anchor				= rtm->anchor;

			//re-initiliase thread
			initAnchorThread(tvm, rtm);
			thread					= rtm->temp;
			thread_byteIndex		= thread->p.byteIndex;
			thread_programCounter	= thread->p.programCounter;
			programStart			= thread_programCounter;
			thread_flags			= thread->p.flags;
			thread_previousByte		= thread->p.previousByte;

		} else {
			// quick loop to next anchor point
			thread_byteIndex		= rtm_anchor;
			thread_programCounter	= programStart;
			if ((rtm_anchor + rtm_endianMask) >= rtm_end) {
				thread_flags		= VMFL_ANCHOR + VMFL_END;
			} else {
				thread_flags	    = VMFL_ANCHOR;
			}
			thread->p.highwaterGroup  = 0;
			thread->p.startedMask     = 0;
			thread->p.markedMask	  = 0;
			thread->p.sequenceCount   = 0;
			thread->p.context		  = 0;
			thread_previousByte		  = INVALID_BYTE_ADDRESS;

			// update anchor guard with best constraints
			// similar to update on character fail

			for (i=0; i<rtm->guardCount; i++) {
				anchor = &rtm->anchorGuard[i];
				if (anchor->constrained_end == INVALID_BYTE_ADDRESS) {
					anchor->constrained_start = anchor->new_start;
					anchor->constrained_end   = anchor->new_end;
				} else if (!((int) anchor->new_end < (int) anchor->constrained_start)) {
					if ((int) anchor->new_start > (int) anchor->constrained_end + 1) {
						anchor->constrained_start = anchor->new_start;
						anchor->constrained_end   = anchor->new_end;
					} else {
						if ((int) anchor->new_start < (int) anchor->constrained_start) anchor->constrained_start = anchor->new_start;
						if ((int) anchor->new_end   > (int) anchor->constrained_end)   anchor->constrained_end   = anchor->new_end;
					}
				}
				rtm->anchorGuard[i].new_end = INVALID_BYTE_ADDRESS;
			}
		} 
	}
}
