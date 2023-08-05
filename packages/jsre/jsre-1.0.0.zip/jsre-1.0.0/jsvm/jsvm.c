/* **********************************************************

    Jigsaw Virtual Machine (Jsvm) Python Wrapper
    
    This wraps the VM as a Python Extension type
    
    @author: Howard Chivers
    @version: 1.1.3
    
	Copyright (c) 2015, Howard Chivers
	All rights reserved.

************************************************************ */

#include <Python.h>
#include "jsvm.h"

#define VERSION "1.1.3"
#define MODULE_SUMMARY "jigsawvm provides C extension methods for searching byte streams, including a NFA for unicode RE searches"

#define JIGSAWTVM_SUMMARY "Jigsawvm provides a fast table-driven NFA for RE forensics"
typedef struct {
	PyObject_HEAD
	VirtualMachine tvm;
} Jigsawtvm;

//*********************************************
// Misc
//*********************************************

static void setError(PyObject * type,char * message,int error) {
	//set the global exception value, will terminate strings at 128 bytes
	char msg[128];
	int res;
	res = snprintf(msg,128,message,error);
	if (res<0) {
		PyErr_SetString(PyExc_SystemError,"jsvm Error while reporting error message");
	} else {
		PyErr_SetString(type,msg);
	}
	return;
}

static int pyListtoCArray(PyObject * list, uint32_t * dest, int length) {
	// convert list of python integers to array of uint32_t
	PyObject * pint;
	int i;

	for (i=0; i<length; i++) {
		pint = PyList_GetItem(list, i);
		if (pint == NULL) {
			PyErr_SetString(PyExc_SystemError,"jsvm wrapper error in list conversion, python list too short?");
			return 1;
		}
		dest[i] = PyLong_AsUnsignedLong(pint);	
	}
	return 0;
}

static PyObject * pyListFromArray(uint32_t * src, int length) {
	// build new python list with C array values
	int i, res;
	PyObject * list;
	PyObject * pint;
	
	list = PyList_New(0);
	for (i=0; i<length; i++) {

		pint = PyLong_FromUnsignedLong(src[i]);
		if (pint == NULL) {
			Py_DECREF(list);
			PyErr_SetString(PyExc_SystemError,"jsvm wrapper error in building python list conversion, failed to convert input value");
			return NULL;
		}

		res = PyList_Append(list, pint);
		if (res) {
			setError(PyExc_SystemError,"Error from jsvm.__getstate__: failed to append bytecode, code: %i",res);
			Py_DECREF(list);
			return NULL;
		}
	}
	return list;
}

static ByteCode * convertProgramList(PyObject * list) {
	//convert python list of tuples to array of State
	int len, i, last;
	ByteCode * res;
	PyObject * tup;
    unsigned short instruction, index, address;

	if (!PyList_Check(list)) {
		PyErr_SetString(PyExc_ValueError,"Call to jsvm.newProgram() not a Python list");
		return NULL;
	}
	
	len = PyList_Size(list);
	if (len<0) {
		PyErr_SetString(PyExc_ValueError,"Call to jsvm.newProgram() not a list");
		return NULL;
	}
	if (len==0) {
		PyErr_SetString(PyExc_ValueError,"Call to jsvm.newProgram() with empty list");
		return NULL;
	}

	res = (ByteCode *) malloc(len * sizeof(ByteCode));
	if (res==NULL) {
		PyErr_NoMemory();
		return NULL;
	}

	for (i=0;i<len;i++) {
		tup = PyList_GetItem(list,i);
		if (tup==NULL) {
			free(res);
			return NULL; //out of bounds error?
		}

		//check for tuple?
		if (!PyTuple_Check(tup)) {
			PyErr_SetString(PyExc_ValueError,"Element in jsvm program list is not a tuple");
			free(res);
			return NULL;
		}
    
		//load tuple into c structure
		if (!PyArg_ParseTuple(tup, "HHHp", &instruction, &index, &address, &last)) {
			PyErr_SetString(PyExc_ValueError,"Invalid entries in jsvm program list tuple");
			return NULL;
		}
        res[i].instruction = (uint8_t) (0xFFFF & instruction);
        res[i].index       = (uint8_t) (0xFFFF & index);
        res[i].address     = (uint16_t) (0xFFFFFFFF & address);
		if (last) res[i].instruction |= FLAG_FINAL;
	}
	return res;
}

//*********************************************
// Public methods in module
//*********************************************

#define VERSION_SUMMARY "string version()   Provides version string for module."
static PyObject *jigsawtvm_version(PyObject *self, PyObject *args) {
	//provide module version string
    return Py_BuildValue("s",VERSION);
}

#define FINDBYTE_SUMMARY "int findByte(buffer,start,stop,target)   Finds next position of tagret byte in a byte buffer."
static PyObject *jigsawtvm_findByte(PyObject *self, PyObject *args) {
	//quick buffer search for a byte, returns location of byte or -1 (not found)
	//params:
    Py_buffer buffer;	//raw bytes to be searched
	int start;          //start position for search
	int stop;           //stop position for search
	char target;        //target of search
	//
	int res;

    if (!PyArg_ParseTuple(args, "y*iib", &buffer, &start, &stop, &target)) {
        PyBuffer_Release(&buffer);
		PyErr_SetString(PyExc_ValueError,"jsvm.findByte() called with invalid arguments");
        return NULL;
    }
    res = findByte((uint8_t *)(buffer.buf),start,stop,target);
    PyBuffer_Release(&buffer);
    return Py_BuildValue("i", res);
}

#define COUNTBYTE_SUMMARY "int countByte(buffer,start,stop,target)   Counts number of target bytes in a byte buffer."
static PyObject *jigsawtvm_countByte(PyObject *self, PyObject *args) {
	//counts number of occurrances of particular byte in a buffer
	//Params:
	Py_buffer buffer;	//raw bytes to be searched
	int start;          //start position for search
	int stop;           //stop position for search
	char target;        //target of search
	//
    int res,count;

    if (!PyArg_ParseTuple(args, "y*iib", &buffer, &start, &stop, &target)) {
        PyBuffer_Release(&buffer);
        return NULL;
    }
    count = 0;
    while (start<stop) {
        res = findByte((buffer).buf,start,stop,target);
        if (res == -1) {
            break;
        } else {
            start = res + 1;
            count++;
        }
    }
    PyBuffer_Release(&buffer);
    return Py_BuildValue("i", count);
}

//**********************************************
// Object Management
//**********************************************

static void jigsawtvm_dealloc(Jigsawtvm * self) {
	//free machine space
	freeMachine(&(self->tvm));
}

static PyObject * jigsawtvm_new(PyTypeObject *type, PyObject *args, PyObject *kwds) {
	//build machine space
	Jigsawtvm * self;
	int res;

	self = (Jigsawtvm *)type->tp_alloc(type,0);
	res = allocateMachine(&(self->tvm));
	if (res) {
		//allocation exception - on error allocate machine will have already freed any machine mallocs
		PyErr_NoMemory();
		Py_DECREF(self);
		return NULL;
	}
	return (PyObject *) self;
}

static int jigsawtvm_init(Jigsawtvm * self, PyObject *args, PyObject *kwds) {
	//Init takes no arguments. 

	if (self->tvm.startList==NULL) {
		PyErr_SetString(PyExc_SystemError,"Invalid call to jsvm.__init__, jsvm object does not exist");
		return -1;
	}

    self->tvm.stateLength        = 0;
    self->tvm.programLength		 = 0;
    self->tvm.startLength        = 0;

	return 0;
}

//**********************************************************
// Class Methods
//**********************************************************

#define GETSTATE_SUMMARY "__getstate__()  returns serialisable state" 
static PyObject *jigsawtvm_getstate(Jigsawtvm *self, PyObject *args) {
	// no inputs
	PyObject * state;
	PyObject * size;
	PyObject * starts;
	PyObject * submasks;
	PyObject * program;
	PyObject * transitions;
	uint32_t i;
	uint16_t instruction, halt;
	int res;

	// required transition size
	i  = self->tvm.stateLength;
	size =  Py_BuildValue("k", i);

	// other state in lists
	transitions = PyList_New(0);
	program = PyList_New(0);
	starts = PyList_New(0);

	// output non-fail values from state table
	for(i = 0; i < self->tvm.stateLength << 8; i++) {
		if(self->tvm.transition[i] != CHARACTER_FAIL) {
			res = PyList_Append(transitions, Py_BuildValue("kI", i, self->tvm.transition[i]));
			if (res) {
				setError(PyExc_SystemError,"Error from jsvm.__getstate__: failed to append transition, code: %i",res);
				goto abort;
			}
		}
	}

	// unload program into list of bytecode tuples
	for(i = 0; i < self->tvm.programLength; i ++) {
		instruction = self->tvm.program[i].instruction;
		halt        = FALSE;
		if (instruction & FLAG_FINAL) {
			halt        = TRUE;
			instruction = instruction & ~FLAG_FINAL;
		}
		res = PyList_Append(program, Py_BuildValue("HHHH", instruction, self->tvm.program[i].index, self->tvm.program[i].address, halt));
		if (res) {
			setError(PyExc_SystemError,"Error from jsvm.__getstate__: failed to append bytecode, code: %i",res);
			goto abort;
		}
	}

	//unload starts into list of start tuples

	for(i = 0; i < self->tvm.startLength; i ++) {
		submasks = pyListFromArray(self->tvm.startList[i].subgroupMasks, MAX_MARKS);
		if (submasks == NULL) {
			setError(PyExc_SystemError,"Error from jsvm.__getstate__: failed to build submask list from start", 0);
			goto abort;
		}
		res = PyList_Append(starts, Py_BuildValue("kkkkkkkO", self->tvm.startList[i].command, 
															  self->tvm.startList[i].address, 
													 	      self->tvm.startList[i].returnPairCount,
														      self->tvm.startList[i].offset,
														      self->tvm.startList[i].stride,
														      self->tvm.startList[i].guardCount,
															  self->tvm.startList[i].backrefMask,
															  submasks));
		Py_DECREF(submasks);
		if (res) {
			setError(PyExc_SystemError,"jsvm.__getstate__ error while building start list, code: %i",res);
			goto abort;
		}

    }
	state = Py_BuildValue("OOOO", size, starts, program, transitions);
	if (state == NULL) goto abort;

	Py_DECREF(size);
	Py_DECREF(starts);
	Py_DECREF(program);
	Py_DECREF(transitions);
	return state;

abort:
	Py_DECREF(size);
	Py_DECREF(starts);
	Py_DECREF(program);
	Py_DECREF(transitions);
    return NULL;
}


#define SETSTATE_SUMMARY "__setstate__()  loads serialisable state" 
static PyObject *jigsawtvm_setstate(Jigsawtvm *self, PyObject *args) {
    PyObject * state;
	PyObject * starts;
	PyObject * pmasklist;
	PyObject * program;
	PyObject * transitions;
	Py_ssize_t length, k;
	int res;
	unsigned long address, size, transition;
	unsigned long sadd, scmd, sret, soff, ssde, sgdc, sbrm;
	Start start;
	ByteCode * proglist;					

    /* assumes state is provided as a single python object */
    
    if (!PyArg_ParseTuple(args, "O", &state)) {
        return NULL;
    }

	if (!PyArg_ParseTuple(state, "kOOO", &size, &starts, &program, &transitions)) {
        Py_DECREF(state);
        return NULL;
    }
    
	// rebuild state size
	res = newStates(&(self->tvm), 0, size);
	if (res) {
		setError(PyExc_SystemError,"Error from jsvm.__setstate__.newStates, code: %i",res);
		return NULL;
	}

	// write transitions back to table
	length = PyList_Size(transitions);   
	for (k = 0; k < length; k++) {
		if (!PyArg_ParseTuple(PyList_GetItem(transitions, k),"kk", &address, &transition)) {
			return NULL;
		}
		res = newTransitionRange(&(self->tvm), address >> 8, address & 0xFF, address & 0xFF, (uint16_t) transition);
		if (res) {
			setError(PyExc_SystemError,"Error from jsvm.__setstate__.newTransitionRange(), code: %i",res);
			return NULL;
		}
	}

	// load program from bytecode tuples
	proglist = NULL;
	proglist = convertProgramList(program);
	if (proglist==NULL) return NULL;

	length	 = PyList_Size(program);
	res		 = newProgram(&(self->tvm), proglist, length);
	if (proglist!=NULL) free(proglist);
	if (res) {
		setError(PyExc_SystemError,"Error from jsvm.__setstate__.newProgram(), code: %i",res);
		return NULL;
	}
	
	// load starts
	length = PyList_Size(starts);   
	for (k = 0; k < length; k++) {
		if (!PyArg_ParseTuple(PyList_GetItem(starts, k), "kkkkkkkO", &scmd, &sadd, &sret, &soff, &ssde, &sgdc, &sbrm, &pmasklist)) {
			PyErr_SetString(PyExc_ValueError,"jsvm.__setstate__ invalid entries in Start tuple");
			return NULL;
		}

		start.command	  = scmd;
		start.address	  = sadd;
		start.returnPairCount = sret;
		start.offset	  = soff;
		start.stride	  = ssde;
		start.guardCount  = sgdc;
		start.backrefMask = sbrm;

		res = pyListtoCArray(pmasklist, start.subgroupMasks, MAX_MARKS);
		if (res) {
			return NULL;
		}

		res = newStart(&(self->tvm), k, start);
		if (res) {
			setError(PyExc_SystemError,"Error from jsvm.__setstate__.newStart(), code: %i",res);
			return NULL;
		}
	}
	Py_RETURN_NONE;
}

#define NEXTSTATE_SUMMARY "nextState()  returns index of next uninitialised state" 
static PyObject *jigsawtvm_nextState(Jigsawtvm *self, PyObject *args) {
    return Py_BuildValue("i", self->tvm.stateLength);
}

#define NEXTPROGRAM_SUMMARY "nextProgramAddress()  returns index of next program address" 
static PyObject *jigsawtvm_nextProgramAddress(Jigsawtvm *self, PyObject *args) {
    return Py_BuildValue("i", self->tvm.programLength);
}

#define NEXTSTART_SUMMARY "nextStart()  returns index of next available start" 
static PyObject *jigsawtvm_nextStart(Jigsawtvm *self, PyObject *args) {
    return Py_BuildValue("i", self->tvm.startLength);
}

#define SETTRACE_SUMMARY "setTrace(mode)  switches on state trace mode for debugging" 
static PyObject *jigsawtvm_setTrace(Jigsawtvm *self, PyObject *args) {
	unsigned long mode;
	if (!PyArg_ParseTuple(args, "k", &mode)) {
		PyErr_SetString(PyExc_ValueError,"jsvm.setTrace() called with invalid arguments");
        return NULL;
    }
    setTrace(&(self->tvm), mode);
	Py_RETURN_NONE;
}

#define NEWSTATES_SUMMARY "newStates(start,stop)  build new states from start to stop-1"
static PyObject *jigsawtvm_newStates(Jigsawtvm *self, PyObject *args) {
	//builds a set of new states from start to end-1
	//params:	
	unsigned long start, stop;		//first/last state to be built+1 (last built is stop-1)
	//
	int res;

	if (!PyArg_ParseTuple(args, "kk", &start, &stop)) {
		PyErr_SetString(PyExc_ValueError,"jsvm.newStates() called with invalid arguments");
        return NULL;
    }
	
	res = newStates(&(self->tvm), start, stop);
	if (res) {
		setError(PyExc_SystemError,"Error from jsvm.newState(), code: %i",res);
		return NULL;
	}
	Py_RETURN_NONE;
}

#define NEWTRANSITIONRANGE_SUMMARY "newTransitionRange(state,startRange,endRange,transition)  assign transition from state for each value in range, inclusive"
static PyObject *jigsawtvm_newTransitionRange(Jigsawtvm *self, PyObject *args) {
	//Specifies a new tranistion
	//params:		
	unsigned long state;	    //the state number
	unsigned long startRange; 	//start of byte range
	unsigned long endRange;     //end of byte range inclusive
	unsigned int  transition;	//the state or stat expand address which is the target of the tranistion
	//
	int res;

	if (!PyArg_ParseTuple(args, "kkkI", &state, &startRange, &endRange, &transition)) {
		PyErr_SetString(PyExc_ValueError,"jsvm.newTransactionRange() called with invalid arguments");
        return NULL;
    }

	res = newTransitionRange(&(self->tvm),state,startRange,endRange,(uint16_t)transition);
	if (res) {
		setError(PyExc_SystemError,"Error from jsvm.newTransaction(), code: %i",res);
		return NULL;
	}
	Py_RETURN_NONE;
}

#define NEWTRANSITION_SUMMARY "newTransition(state,bytes,transition) assign transition from state for each byte"
static PyObject *jigsawtvm_newTransition(Jigsawtvm *self, PyObject *args) {
	//Specifies a new tranistion
	//params:		
	unsigned long state;	  //the state number
	Py_buffer buffer;		  //a byte array, each value of which triggers the same transition
	unsigned int transition;  //the state which is the target of the transition
	//
	int res;

	if (!PyArg_ParseTuple(args, "ky*I", &state, &buffer, &transition)) {
		PyErr_SetString(PyExc_ValueError,"jsvm.newTransaction() called with invalid arguments");
        return NULL;
    }

	res = newTransition(&(self->tvm),state,(uint8_t *)(buffer.buf),buffer.len,(uint16_t)transition);
	PyBuffer_Release(&buffer);
	if (res) {
		setError(PyExc_SystemError,"Error from jsvm.newTransaction(), code: %i",res);
		return NULL;
	}
	Py_RETURN_NONE;
}

#define NEWPROGRAM_SUMMARY "int newProgram(ProgList) write a program to the vm, returns the base address at which it was written"
static PyObject *jigsawtvm_newProgram(Jigsawtvm *self, PyObject *args) {
	//Specifies a new program - a list of (Instuction,Index,Address,Last) tuples 
	//params:
	uint32_t length,baseAddress;		//number of instructions to output, base address
	PyObject * pPlist;					//python program list
	ByteCode * Plist;					//c program list
	//
	int res;

	if (!PyArg_ParseTuple(args, "O",&pPlist)) {
		PyErr_SetString(PyExc_ValueError,"jsvm.newStateExpansion() called with invalid arguments");
        return NULL;
    }

	Plist = NULL;
	//convert python tuple conversions

	Plist		= convertProgramList(pPlist);
	if (Plist==NULL) return NULL;
	length		= PyList_Size(pPlist);
	baseAddress = self->tvm.programLength;

	res			= newProgram(&(self->tvm),Plist,length);
	if (Plist!=NULL) free(Plist);

	if (res) {
		setError(PyExc_SystemError,"Error from jsvm.newProgram(), code: %i",res);
		return NULL;
	}

    return Py_BuildValue("I", baseAddress);
}

#define NEWSTART_SUMMARY "int newStart(startTuple)   load start tuple (command,address,matchPairCount,offset,stride,guardCount,backrefMasks,reservedMatch), return ID"
static PyObject *jigsawtvm_newStart(Jigsawtvm *self, PyObject *args) {
	//specify start expansion for new re
	//params:
	uint32_t startIndex;		// ID of the new re
	PyObject * pStart;			// Start tuple(command,address,offset,stride)
	PyObject * pmasklist;		// python subgroupMask list
	unsigned long sadd, scmd, sret, soff, ssde, sgdc, sbrm;
	int res;
	//
	Start start;

	if (!PyArg_ParseTuple(args, "iO", &startIndex, &pStart)) {
		PyErr_SetString(PyExc_ValueError,"jsvm.newStart() called with invalid arguments");
        return NULL;
	}

	//check for tuple?
	if (!PyTuple_Check(pStart)) {
		PyErr_SetString(PyExc_ValueError,"jsvm.newStart() Start value is not a tuple");
		return NULL;
	}
	if (!PyArg_ParseTuple(pStart,  "kkkkkkkO", &scmd, &sadd, &sret, &soff, &ssde, &sgdc, &sbrm, &pmasklist)) {
		PyErr_SetString(PyExc_ValueError,"jsvm.newStart() called with invalid entries in Start tuple");
        return NULL;
	}
	start.command	  = scmd;
	start.address	  = sadd;
	start.returnPairCount = sret;
	start.offset	  = soff;
	start.stride	  = ssde;
	start.guardCount  = sgdc;
	start.backrefMask = sbrm;

	res = pyListtoCArray(pmasklist, start.subgroupMasks, MAX_MARKS);
	if (res) {
		return NULL;
	}

	startIndex = self->tvm.startLength;
	res = newStart(&(self->tvm),startIndex,start);
	if (res) {
		setError(PyExc_SystemError,"Error from jsvm.newStart(), code: %i",res);
		return NULL;
	}
	return  Py_BuildValue("I", startIndex);
}

#define FINDMATCH_SUMMARY "tuple findMatch(buffer,start,stop,end,search)  runs re and returns list of tuples (re,start,end); search true->first match only"
PyObject *jigsawtvm_findMatch(Jigsawtvm *self, PyObject *args) {
	/*
	applies the re to the buffer and returns a list of tuples of match positions (re,(start,stop)....)
	the number returned depends on the pair count set in the start. 
	match 0,1 are always returned
	returned values are corrected to python specs: the high value is exclusive
	*/
	//params
	Py_buffer pBuffer;	//raw bytes to search
	// start;			//first anchor position in buffer
	// stop;			//last anchor position +1
	// end;				//actual end of buffer+1
	//
	Runtime rtm;
	Start start;
	uint32_t mask;
	int i,res,toReturn, mark_end, mark_start;
	unsigned long bufstart, bufstop, bufend;
	bool search;
	PyObject * resultList;			//a list of results, this is returned
	PyObject * result;				//result contains [re,(match 0)(match 1) ....]
	PyObject * value;				//match tuple     (first,last+1)

	res = allocateRuntime(&rtm);
	if (res) {
		//allocation exception
		PyErr_NoMemory();
		Py_DECREF(self);
		return NULL;
	}

    if (!PyArg_ParseTuple(args, "y*kkkp", &pBuffer, &bufstart, &bufstop, &bufend, &search)) {
        PyBuffer_Release(&pBuffer);
		PyErr_SetString(PyExc_ValueError,"jsvm.findMatch() called with invalid arguments");
		freeRuntime(&rtm);
		Py_DECREF(self);
        return NULL;
	}

	rtm.bufferSpec.start = bufstart;
	rtm.bufferSpec.stop  = bufstop;
	rtm.bufferSpec.end   = bufend;

	resultList = PyList_New(0);
	initRunTime(&(self->tvm),&rtm,0);

	do  {
		//next match
		res = findNextMatch(&(self->tvm),&rtm,(uint8_t *)(pBuffer.buf));
		if (res) {
			setError(PyExc_SystemError,"Error from jsvm.findMatch(), code: %i",res);
			goto abort;
		}
        
		if (!rtm.published) break;

		start		= self->tvm.startList[rtm.pubReIndex];
		toReturn	= start.returnPairCount;
		if (toReturn<1) toReturn = 1;

		//build base result list (with re)
		result	= PyList_New(0);
		res		= PyList_Append(result,Py_BuildValue("I",rtm.pubReIndex));
		if (res) {
			Py_DECREF(result);
    		goto abort;
    	}

		//add match tuples
		mask = 1;
		for (i=0;i<toReturn;i+=1) {
			mark_start = rtm.groupMark[i].start;
			mark_end   = rtm.groupMark[i].end;
			if (!(rtm.published & mask)) {
				value = Py_BuildValue("ii", -1, -1);
			} else if ((i == (toReturn - 1)) && (start.command & RESERVED_MATCH)) {
				value = Py_BuildValue("ii", mark_start, mark_end);
			} else {
				value = Py_BuildValue("ii", mark_start, mark_end + 1);
			}
			mask = mask << 1;
			res = PyList_Append(result,value);
			Py_DECREF(value);
    		if (res) {
				PyErr_SetString(PyExc_ValueError,"jsvm.findMatch() failed to append match to result list");
				Py_DECREF(result);
    			goto abort;
    		}
		}

    	//add to result list
    	res = PyList_Append(resultList,result);
		Py_DECREF(result);
    	if (res) {
    		goto abort;
    	}
		if (search) break;   //return only first result 
	} while (rtm.published);

	freeRuntime(&rtm);
	PyBuffer_Release(&pBuffer);
	return resultList;

abort:
	freeRuntime(&rtm);
	PyBuffer_Release(&pBuffer);
	Py_DECREF(resultList);
	return NULL;
}

//******************************************************************
// Formal class/module specs
//******************************************************************

static PyMethodDef jigsawtvm_module_methods[] = {
    { "version",jigsawtvm_version, METH_NOARGS, VERSION_SUMMARY },
    { "findByte",jigsawtvm_findByte, METH_VARARGS, FINDBYTE_SUMMARY },
    { "countByte",jigsawtvm_countByte, METH_VARARGS, COUNTBYTE_SUMMARY },
    { NULL, NULL,}
};

static PyMethodDef jigsawtvm_object_methods[] = {
	{ "__getstate__",(PyCFunction)jigsawtvm_getstate,METH_VARARGS,GETSTATE_SUMMARY },
	{ "__setstate__",(PyCFunction)jigsawtvm_setstate,METH_VARARGS,SETSTATE_SUMMARY },
    { "nextState",(PyCFunction)jigsawtvm_nextState,METH_VARARGS,NEXTSTATE_SUMMARY },
    { "nextProgramAddress",(PyCFunction)jigsawtvm_nextProgramAddress,METH_VARARGS,NEXTPROGRAM_SUMMARY },
    { "nextStart",(PyCFunction)jigsawtvm_nextStart,METH_VARARGS,NEXTSTART_SUMMARY },
	{ "setTrace",(PyCFunction)jigsawtvm_setTrace,METH_VARARGS,SETTRACE_SUMMARY },
	{ "newStates",(PyCFunction)jigsawtvm_newStates,METH_VARARGS,NEWSTATES_SUMMARY },
	{ "newTransitionRange",(PyCFunction)jigsawtvm_newTransitionRange,METH_VARARGS,NEWTRANSITIONRANGE_SUMMARY },
	{ "newTransition",(PyCFunction)jigsawtvm_newTransition,METH_VARARGS,NEWTRANSITION_SUMMARY },
	{ "newProgram",(PyCFunction)jigsawtvm_newProgram,METH_VARARGS,NEWPROGRAM_SUMMARY },
	{ "newStart",(PyCFunction)jigsawtvm_newStart,METH_VARARGS,NEWSTART_SUMMARY },
	{ "findMatch",(PyCFunction)jigsawtvm_findMatch,METH_VARARGS,NEWSTART_SUMMARY },
    { NULL, NULL,}
};

static PyTypeObject jigsawtvmType = {
			PyVarObject_HEAD_INIT(NULL, 0)
			"jsvm.Jsvm",			        /* tp_name */
			sizeof(Jigsawtvm),				/* tp_basicsize */
			0,								/* tp_itemsize */
			(destructor)jigsawtvm_dealloc,	/* tp_dealloc */
			0,								/* tp_print */
			0,								/* tp_getattr */
			0,								/* tp_setattr */
			0,								/* tp_reserved */
			0,								/* tp_repr */
			0,								/* tp_as_number */
			0,								/* tp_as_sequence */
			0,								/* tp_as_mapping */
			0,								/* tp_hash */
			0,								/* tp_call */
			0,								/* tp_str */
			0,								/* tp_getattro */
			0,								/* tp_setattro */
			0,								/* tp_as_buffer */
			Py_TPFLAGS_DEFAULT,				/* tp_flags */
			JIGSAWTVM_SUMMARY,				/* tp_doc */
			0,								/* tp_traverse */
			0,								/* tp_clear */
			0,								/* tp_richcompare */
			0,								/* tp_weaklistoffset */
			0,								/* tp_iter */
			0,								/* tp_iternext */
			jigsawtvm_object_methods,		/* tp_methods */
			0,								/* tp_members */
			0,								/* tp_getset */
			0,								/* tp_base */
			0,								/* tp_dict */
			0,								/* tp_descr_get */
			0,								/* tp_descr_set */
			0,								/* tp_dictoffset */
			(initproc)jigsawtvm_init,		/* tp_init */
			0,								/* tp_alloc */
			jigsawtvm_new,					/* tp_new */
};

static struct PyModuleDef jigsawtvmModule = {
    PyModuleDef_HEAD_INIT,
    "jsvm",
    MODULE_SUMMARY,
    -1,
    jigsawtvm_module_methods,
    NULL,
    NULL,
    NULL,
    NULL
};

PyMODINIT_FUNC PyInit_jsvm(void) {
	PyObject* m;

	if (PyType_Ready(&jigsawtvmType) < 0)
	return NULL;

	m = PyModule_Create(&jigsawtvmModule);
	if (m == NULL)
	return NULL;

	Py_INCREF(&jigsawtvmType);
	PyModule_AddObject(m, "Jsvm", (PyObject *)&jigsawtvmType);
	return m;
}









