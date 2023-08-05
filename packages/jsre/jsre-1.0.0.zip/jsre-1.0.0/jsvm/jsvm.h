/* **********************************************************

    Jigsaw Virtual Machine (jsvm) Header

	@author: Howard Chivers
    @version: 1.1.3
    
    Copyright (c) 2015, Howard Chivers
	All rights reserved.
    
************************************************************ */

/*
	Changes

	V 1.1.0
	*******
	Threadheap size increased to 4096
	Error numbering restructured
	New start commands:
		FIXED_ANCHOR  - prevents anchor increment for this re
		NOINC_ANCHOR  - pevents normal anchor inc but allows next byte after publish
	Thread heap management rewritten - sorted list rather than linked list to allow binary searches

    V 1.1.1
    *******
    __getstate__    __setstate__  added to wrapper
    verbose/nonverbose option added to trace for profiling
	test end of buffer now checks bytecounter as well as flag
	stop and end refactored - now exclusive
	updated lazy prioritisation mechanism - policy rather than trace dump
	protection against infinite loops (but all loops must use counting to use it)
	added backreference test
	incremental allocation of major memory items (state, program, heap)

	V 1.1.2
	*******
	bugfix - ref counting on __setstate__/__getstate__
	update all wrapper types (conservative platform portability)
	include 'jsvm.' in all exception messages


	V 1.1.3
	*******
	input position reset (for re lookahead)
	unmeasured count restored
	small improvement in choice of thread to dump following collision 
	(if no comparable marked submatches, choose thread with leftmost mark)
	zero guards after publish
	protection of backreference threading
	max threadheap now 8192
	group mark masks to specify how groups are nested 
	(reset started and marked masks on entering group - doesn't retain previous sub-group hits in loop)
	guard ranges to allow guarded loops within epxressions,not just at start
*/

#include <string.h>
#include <stdint.h>

typedef int bool;
#define TRUE  1
#define FALSE 0
#define INVALID_BYTE_ADDRESS 0xFFFFFFFF
#define COUNT_UNMEASURED	0xFFFF			// this counter value will not be decremented by counter test 

// configuration sizes
#define INIT_STATE_SIZE	        64          // initial table size in states
#define STATE_SIZE_INC         512	        // table allocation increments
#define MAX_STATE_SIZE       16384          // number of character entries possible in table
#define INIT_BYTECODE_SIZE	  1024			// initial program size in instructions
#define BYTECODE_SIZE_INC	  1024			// program allocation increments
#define MAX_BYTECODE_SIZE	 49152			// maximum byteCode length in instructions
#define START_LIST_SIZE         64			// startList size
#define INIT_THREADHEAP_SIZE   256          // size of initial working heap
#define MAX_THREADHEAP_SIZE	   8192          // final possible allocation size of threadheap
#define MAX_COUNTERS		  	 4			// number of counters allowed
#define MAX_MARKS			    32			// number of pairs of marks allowed
#define MAX_SEQUENCE			32			// allocated space to record group encounter order
#define LOOKBEHIND_LIMIT	 	 5			// number of bytes that may be backed up to find previous character start

// bytecodes
#define INSTRUCTION_MASK    0x7F			// normal instructions
#define FLAG_FINAL			0x80			// flags last instruction

// test charecter instuction
#define INSTR_CHARACTER		0x20			// a character [group], if set then ...
#define FLAG_SET_GUARD	    0x10            // move the next anchor to the point after this character, if character fails
#define FLAG_ZERO_WIDTH		0x8				// do not auto-increment with the character byte width, just test
#define FLAG_CONTINUE		0x4				// a match fail will allow the stream to continue (but not consume bytes) and just set flags
#define FLAG_PREVIOUS		0x2				// test previous character
#define FLAG_BRANCH		    0x1			    // branch on fail to short forward offset (program counter + code.index)

// test instruction
#define INSTR_TEST			0x40			// test instuction. Will branch to address on success. Function is controlled by flags: that follow:
											// note that no test flag set = unconditional jump, only FLAG_NOT set -> NOP
#define FLAG_TEST_NOT		0x01			// invert decision action, branch on false
#define FLAG_TEST_FLAGS     0x02			// test VM flags masked by index byte (if several flags masked, test ok if any are set)
#define FLAG_TEST_COUNT	     0x04			// decrement counter and branch if zero
#define FLAG_TEST_GUARD     0x08			// test if anchor guard is passed and sets the guard index for this thread
#define FLAG_TEST_BACK		0x10			// test if current input matches previously recorded mark

// other instructions
// (warning - check code for detection of index/address using bits 0,1 before adding new instruction)
#define INSTR_NEW_THREAD	0x1				// write temp state to new thread, with given prog start address
#define INSTR_RESET_TO_MARK 0x2				// set the byte pointer to the indexed start mark
#define INSTR_SET_COUNT		0x3				// set indexed counter to value
											// (Note - if counter value is COUNT_UNMEASURED counter will not be decremented)
#define INSTR_PUBLISH		0x4				// publish (write marked locations to result)
#define INSTR_SCAN	        0x5				// scan anchor until character matches, mark 0 on success
#define INSTR_SET_CONTEXT   0x6			    // set indexed context and also mark start (write current byte address to indexed mark start)
#define INSTR_SET_MARK		0x7				// set indexed mark to value
#define INSTR_MARK_START	0xA				// write current byte address to indexed mark start
#define INSTR_MARK_END      0xE				// write current byte address to indexed mark end

// virtual machine flags
#define VMFL_CHARACTER_OK	0x1				// last character tested OK
#define VMFL_START			0x2				// at buffer start (not just a new anchor)
#define VMFL_ANCHOR			0x4				// at new anchor
#define VMFL_END			0x8				// at end of buffer
#define VMFL_PUBLISHED		0x10		    // this new anchor follows a published match

// group sequence flags
#define INVALID_START_INDEX	0xFFFF			// this start not recorded in index
#define OPEN_GROUP_FLAG		0x8000			// this group index is group start (false is group end)
#define GROUP_INDEX_MASK	0x0FFF			// group number mask in flag

// detect index/address
#define INSTR_REQUIRES_INDEX   0x2			// detect index instuctions
#define INSTR_REQUIRES_ADDRESS 0x11         // detect address instructions - test characer or bit 1 set
#define FLAG_MASK		  ~(FLAG_COUNT | FLAG_NOT)   // mask allowed count bits (currently 6 bit) & flags

// character transition codes (allow up to 2**16 -3 transition tables)
#define CHARACTER_FAIL	    0xFFFE			// invalid byte marker
#define CHARACTER_OK		0xFFFF			// character tranistion success
#define RESERVED_COMMANDS   2               // number of addresses at top of space reserved for special transition commands

// Start Commands
#define SECTOR				0x8000			// offset and stride will be applied to the buffer spec
											// stride may be used without this flag, but if so the vm
											// expects stride to be anchor move for the encoding (eg 2 for utf16)
#define FIXED_ANCHOR		0x4000			// the anchor will not be incremented - fixed at the start of the buffer
#define NOINC_ANCHOR		0x2000			// the anchor will be restarted to position after publish, but not incremented through buffer
#define RESERVED_MATCH		0x1000			// highest match record is reserved for signalling (normally alt indexes)
#define ENDIAN_MASK			0x000F			// bit mask for little endian encoding (e.g. 0x1 = 16bit, 0x3 = 32 bit)


// trace
#define TRACE_VERBOSE		0x0002			// print readable trace

// Error codes, as far as possible all checking is done in the compiler service routines
// runtime errors
#define INVALID_INSTUCTION_CODE			 1  // runtime: instruction is not in valid list
#define FAILED_TO_ALLOCATE_RUNTIME		 2  // runtime: failed to allocate runtime thread heap
#define THREAD_HEAP_OVERFLOW			 3  // runtime: ran out of thread heap space - ie too many nondeterministic paths at once
#define FAILED_TO_ALLOCATE_THREAD_HEAP	 4  // failed to allocate additional space in thread heap

// loader errors
#define INVALID_SCAN_CHARACTER			10	// address specified in anchor scan is invalid character
#define FAILED_TO_ALLOCATE_MEMORY       11
#define TVM_NOT_INITIALISED             12
#define INVALID_STATE_REQUESTED         13  // request to build non-sequential state
#define TOO_MANY_STATES_REQUESTED       14
#define TRANSITION_TO_UNDEFINED_STATE   15
#define INVALID_START_REQUESTED         16  // request was not the next available start
#define START_REFERENCES_INVALID_PROGRAM 17
#define INVALID_STATE_INDEX_FOR_TRANSITION 18
#define INVALID_CHARACTER_BRANCH	    19  // character test branches outside program
#define INVALID_TESTCHARACTER_ADDRESS	20  // test character instruction references an invalid address
#define INVALID_COUNTER_INDEX			21  // counter instruction has invalid index
#define INVALID_MARK_INDEX				22  // mark instruction has invalid index
#define INVALID_PROGRAM_COUNTER			23  // newThread instruction has program pointer to invalid program address
#define INVALID_JUMP_ADDRESS			24  // testCounter instruction jumps outside current program
#define END_PROGRAM_NOT_DETECTED		25  // program too big or end program not set
#define INVALID_INSTRUCTION				26  // invalid instruction detected (during load)
#define PROGRAM_TOO_BIG					27  // attempt to load a program above the maximum program size
#define INVALID_BACK_INDEX				28  // index is too big for available marks

typedef struct {
	//program instruction 
	uint8_t	  instruction;					// primary byte code
	uint8_t	  index;						// index (used to index mark, context, counter)
	uint16_t  address;						// pointer (used for bytePosition or programCounter)
} ByteCode;

typedef struct {
	//buffer specification
	uint32_t	start;						// first byte to scan
	uint32_t	stop;						// last anchor + 1
	uint32_t	end;						// last byte to scan + 1
} BufferSpec;

typedef struct {
	// group start and end mark used for reporting group matches
	int32_t		start;						// group start
	int32_t		end;						// group end
	uint16_t	index;						// sequence index - ie most recent start for this group
}	GroupMarks;

typedef struct {
	// recording group events at start of expression evaluation (start, end)
	int32_t		posn;						// group start
	int32_t		len;						// group length
	uint16_t	flag;						// flags
}	GroupSeq;

typedef struct ThreadState ThreadState;

struct ThreadParams {
	// Thread parameter list
	int32_t		byteIndex;					// address of next byte in input stream
	int32_t		previousByte;				// previous byte position
	int32_t		programCounter;				// address of the next instruction 
	uint16_t	sequenceCount;				// count of groups in group sequence
	uint16_t	highwaterGroup;				// highest group id recorded
	uint32_t	context;					// bitmap (bit 0 == mark 0) of mark context, if bits set vm will implement non-greedy matches
	uint32_t	startedMask;			    // btmask to show which groups have valid start
	uint32_t	markedMask;					// bitmask to show which groups have valid start and end
	uint16_t	counter[MAX_COUNTERS];		// loop counters
	uint32_t	loopProtect[MAX_COUNTERS];	// byte position in previous loop for infinite loop protection
	uint32_t	guardStart;					// start byte of current guarded loop
	uint16_t	flags;						// 0 = character OK, 1 = start, 2 = anchor, 3 = end
	uint16_t	guardIndex;					// index of current anchor guard control context

};

struct ThreadState {
	// always cloned
	struct ThreadParams	p;					// parameter list

	// clone only active structures
	GroupMarks	groupMark[MAX_MARKS];		// marked group positions for reporting
	GroupSeq	groupSequence[MAX_SEQUENCE];// groups in sequence encountered

	// neven cloned
	ThreadState * next;						// link to next threadstate
};

typedef struct {
	// guard structure - marks start and end of guarded buffer
	// ie areas where assocaited loops will subsequently fail to match
	uint32_t	new_start;
	uint32_t	new_end;
	uint32_t	constrained_start;
	uint32_t	constrained_end;
} AnchorGuard;

typedef struct {
	//runtime state
	ThreadState * free;						// pointer to free list
	ThreadState * temp;						// working state
	ThreadState * allocated_init;			// malloc base of normal thread heap
	ThreadState * allocated_extra;			// malloc base of additional thread heap if required		    
	ThreadState * queue[MAX_THREADHEAP_SIZE]; // sorted queue of pointers to threadheap
	uint32_t	queueLength;				// number of items in thread queue
	AnchorGuard * anchorGuard;				// array of loop guards - mark where bytes have been tested
	uint32_t	guardCount;					// size of anchor guard array	
	//i/O
	GroupMarks	groupMark[MAX_MARKS];		// published group positions
	uint32_t	published;					// bitmask showing which mark pairs are valid
	GroupSeq	groupSequence[MAX_SEQUENCE];// groups in sequence encountered
	uint32_t	sequenceCount;				// count of groups encountered
	uint32_t	pubReIndex;					// the regular expression that caused the publish    
	uint32_t	previousByte;				// start position of last byte tested in published thread	
	BufferSpec  bufferSpec;					// input buffer
	//control params
	uint32_t	startIndex;					// current regular expression (start index)
	uint32_t	command;					// current start command
	uint32_t    endianMask;					// mask for endian
	uint32_t	returnPairCount;			// number of match pairs required in python return
	uint32_t	startAnchor;				// first anchor position in this re
	uint32_t	anchor;						// current anchor
	uint32_t	stride;						// anchor increment
	uint32_t	backrefMask;				// bitmask of match groups referred to by backreference
	uint32_t	subgroupMasks[MAX_MARKS];	// zero specifies groups nested under the indexed group
	uint32_t	stop;						// limit in buffer of anchor (last address + 1)
	uint32_t	end;						// end of buffer (last address + 1)

} Runtime;

typedef struct {
	uint32_t	command;					// start mode for this re
	uint32_t	address;					// address of first program instruction 
	uint32_t	returnPairCount;			// number of match pairs required in python return
	uint32_t	offset;						// offset into buffer to anchor search
	uint32_t	stride;						// increment for subsequent search anchor points
	uint32_t    guardCount;					// number of guarded loops
	uint32_t	backrefMask;				// bitmask of match groups referred to by backreference
	uint32_t	subgroupMasks[MAX_MARKS];	// zero specifies groups nested under the indexed group 
} Start;

typedef struct {
    //primary state machine
    uint16_t     * transition;
    ByteCode     * program;
    Start        * startList;
	uint32_t	   allocatedStates;		    // allocated counts
	uint32_t	   allocatedInstructions;
    uint32_t       stateLength;				// populated counts - space actually used
    uint32_t       programLength;
	uint32_t       startLength;
	uint32_t	   trace;					// trace debug switch (1 = trace program  2 = verbose)
} VirtualMachine;

int findByte(uint8_t * const buffer,int32_t start,int32_t stop,uint8_t test);

int allocateMachine(VirtualMachine * tvm);
int freeMachine(VirtualMachine * tvm);
int allocateRuntime(Runtime * rtm);
int freeRuntime(Runtime * rtm);
int setTrace(VirtualMachine * tvm, uint32_t mode);

int newStates(VirtualMachine * tvm, uint32_t start, uint32_t end);
int newTransitionRange(VirtualMachine * tvm, const uint32_t stateIndex,const uint32_t rangeStart,const uint32_t rangeEnd, const uint16_t transition);
int newTransition(VirtualMachine * tvm, const uint32_t stateIndex,uint8_t * const buffer,const uint32_t length,const uint16_t transition);
int newProgram(VirtualMachine * tvm,ByteCode * const byteCode,const uint32_t length);
int newStart(VirtualMachine * tvm,const uint32_t startIndex,const Start start);

int initRunTime(VirtualMachine * const tvm,Runtime * rtm,const uint32_t start);
int findNextMatch(VirtualMachine * const tvm, Runtime * rtm, uint8_t * const buffer);
