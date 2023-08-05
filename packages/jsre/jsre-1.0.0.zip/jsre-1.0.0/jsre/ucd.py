'''
UCD - utilities to read unicode database files.

@author: Howard Chivers

Copyright (c) 2015, Howard Chivers
All rights reserved.

Note 'PATCH' in comments, review when unicode database is updated, this version 7.0.0
'''

import os
import logging
import shutil
from jsre.charclass import CharClass, newClassFromList, newCasedCharacter, getAny

UCDLog              = logging.getLogger("UCD")

# encodings that are compiled by default
DEFAULT_ENCODINGS   = ('utf_8', 'utf_16_be', 'utf_32_be', 'ascii', 'cp1250', 'cp1251', 'cp1252', 'cp1253', 'cp1254', 'cp1255', 'cp1256', 'cp1257', 'cp1258')

# minimum character anchor stride for encodings, if not included 1 is default
ENCODING_STRIDE     = {'utf_16_le': 2,
                       'utf_16_be': 2,
                       'utf_32_le': 4,
                       'utf_32_be': 4}

# encoding aliases, specify alternative encodings and endian masks for le types
ENCODING_ALIAS      = {'utf_16_le': ('utf_16_be', 1),
                       'utf_32_le': ('utf_32_be', 3)}

#directory structure
UNICODE_ROOT        = 'UnicodeDatabase'
COMPILE_ROOT        = 'JSRE_Compiled'

# UCD core specifications

# types to build - these are internal names with files /specs in separate tables below
BUILD_LIST          = ('script', 'derived_core', 'property', 'general_category', 'numeric_type', 'line_break', 'grapheme_cluster_break')
SCRIPT_EXTENSION_NAME = ('script_extensions')

# ucd namespace/directory structure
UCD_NAMESPACE       = {'script'            : 'script',
                       'script_extensions' : 'script_extensions',
                       'property'          : '',
                       'derived_core'      : '',
                       'general_category'  : 'general_category',
                       'numeric_type'      : 'numeric_type',
                       'line_break'        : 'line_break',
                       'JSRE_Test'         : '',
                       'grapheme_cluster_break' : 'grapheme_cluster_break'
                       }

# ucd reference files
UCD_FILES           = {'script'            : ('Scripts.txt',),
                       'script_extensions' : ('ScriptExtensions.txt',),
                       'derived_core'      : ('DerivedCoreProperties.txt',),
                       'property'          : ('PropList.txt',),
                       'general_category'  : ('extracted', 'DerivedGeneralCategory.txt'),
                       'numeric_type'      : ('extracted', 'DerivedNumericType.txt'),
                       'numeric_value'     : ('extracted', 'DerivedNumericValues.txt'),
                       'line_break'        : ('extracted', 'DerivedLineBreak.txt'),
                       'JSRE_Test'         : ('JSRE_Test', 'Test_Classes.txt'),
                       'Property'          : ('PropList.txt',),
                       'CaseFolding'       : ('CaseFolding.txt',),
                       'PropertyAliases'   : ('PropertyAliases.txt',),
                       'PropertyValueAliases' : ('PropertyValueAliases.txt',),
                       'script_extensions' : ('ScriptExtensions.txt',),
                       'grapheme_cluster_break' : ('auxiliary', 'GraphemeBreakProperty.txt'),
                       'grapheme_break_test' : ('auxiliary', 'GraphemeBreakTest.txt')
                       }

# ucd file parsing specs
UCD_SPECS           = {'script'            : ((0, 'CODERANGE'), (1, 'PropertyName')),
                       'script_extensions' : ((0, 'CODERANGE'), (1, 'PropertyName')),
                       'derived_core'      : ((0, 'CODERANGE'), (1, 'PropertyName')),
                       'property'          : ((0, 'CODERANGE'), (1, 'PropertyName')),
                       'general_category'  : ((0, 'CODERANGE'), (1, 'PropertyName')),
                       'numeric_type'      : ((0, 'CODERANGE'), (1, 'PropertyName')),
                       'numeric_value'     : ((0, 'CODERANGE'), (1, 'PropertyName')),
                       'line_break'        : ((0, 'CODERANGE'), (1, 'PropertyName')),
                       'JSRE_Test'         : ((0, 'CODERANGE'), (1, 'PropertyName')),
                       'Property'          : ((0, 'CODERANGE'), (1, 'PropertyName')),
                       'CaseFolding'       : ((0, 'CODERANGE'), (1, 'type'), (2, 'target')),
                       'PropertyAliases'   : ((0, 'short'), (1, 'long'), (2, 0), (3, 1), (4, 2), (5, 3)),  # numbered are alternatives
                       'PropertyValueAliases' : ((0, 'property'), (1, 'short'), (2, 'long'), (3, 0), (4, 1), (5, 2), (6, 3)),
                       'script_extensions' : ((0, 'CODERANGE'), (1, 'NOPROCESS')),
                       'grapheme_cluster_break' : ((0, 'CODERANGE'), (1, 'PropertyName')),
                       'grapheme_break_test' : ((0, 'NOPROCESS'),)
                       }

# specs for combined classes
COMBINED_GENERAL    =  (  # (property,newName),(list of classes),(list of code points),negate
                       (('gc', 'P'), ('Pc', 'Pd', 'Ps', 'Pe', 'Pi', 'Pf', 'Po'), (), False),
                       (('gc', 'S'), ('Sm', 'Sc', 'Sk', 'So'), (), False),
                       (('gc', 'Z'), ('Zs', 'Zl', 'Zp'), (), False),
                       (('gc', 'C'), ('Cc', 'Cf', 'Cs', 'Co', 'Cn'), (), False),
                       (('gc', 'LC'), ('Ll', 'Lt', 'Lu'), (), False),
                       (('gc', 'L'), ('Lc', 'Lm', 'Lo'), (), False),
                       (('gc', 'M'), ('Mc', 'Me', 'Mn'), (), False),
                       (('gc', 'N'), ('Nd', 'Nl', 'No'), (), False),
                       (('', 'xdigit'), ('decimal_number', 'hex_digit'), (), False),
                       (('', 'alnum'), ('alpha', 'digit'), (), False),
                       (('', 'blank'), ('space_separator',), ('\N{CHARACTER TABULATION}',), False),
                       (('', 'graph'), ('space', 'Control', 'Surrogate', 'Unassigned'), (), True),
                       (('', 'print'), ('graph', 'blank', 'cntrl'), (), False),
                       (('', 'word'), ('alpha', 'Mark', 'digit', 'Connector_Punctuation', 'Join_Control'), (), False),
                       (('', 'newline'), (), ('\u000A', '\u000B', '\u000C', '\u000D', '\u0085', '\u2028', '\u2029'), False),
                       (('', 'crlf'), (), ('\u000D\u000A'), False),
                       (('', 'not_digit'), ('digit',), (), True),
                       (('', 'not_blank'), ('blank',), (), True),
                       (('', 'not_word'), ('word',), (), True)
                       )

# properties and values to be added to namespace
UCD_EXTRA_PROPERTIES = ('any', 'dot_any', 'not_digit', 'not_blank', 'not_word', 'assigned',
                        'ascii', 'xdigit', 'alnum', 'blank', 'graph', 'print', 'word', 'newline',
                        'crlf', 'test_a', 'test_b')
# list of (prop, value) tuples if required
UCD_EXTRA_VALUES     = []


# search order for single named properties (in addition to standard binary properties)
UCD_PROPERTY_SEARCH  = ('script', 'general_category')

__unicodeRoot = os.path.join(os.path.dirname(os.path.abspath(__file__)), UNICODE_ROOT)
__compileRoot = os.path.join(os.path.dirname(os.path.abspath(__file__)), COMPILE_ROOT)

if not os.path.isdir(__unicodeRoot):
    UCDLog.error("Unicode Database not found in installation".format(__unicodeRoot))
    exit(1)
try:
    __installedEncodings = [name for name in os.listdir(__compileRoot) if os.path.isdir(os.path.join(__compileRoot, name))]
except:
    __installedEncodings = []


class UCDLineInput():
    ''' Provide line at a time input from UCD file.

        references a UCDSpec which specifies which fields to extract and
        their names. The result is a directory with integer range entries
        (first and last) and specified fields if fields are present.
        If fields are missing it does not raise exception, but no default
        values are entered
    '''

    def __init__(self, name):
        '''
        Params:
            name           is the (file)name of the UCD data required

        Raises:
            FileNotFound
            IOError        unable to open file
        '''

        #is file present?
        __unicodeRoot = os.path.join(os.path.dirname(os.path.abspath(__file__)), UNICODE_ROOT)
        self.fpath    = os.path.join(__unicodeRoot, *UCD_FILES[name])
        if not os.path.isfile(self.fpath):
            raise FileNotFoundError('Unable to read UCD file {}'.format(self.fpath))

        try:
            self.file = open(self.fpath, 'r')
        except:
            raise IOError("Failed to open input file: ".format(self.fpath))
        self.spec = UCD_SPECS[name]

    def __iter__(self):
        """ iteration initiator """
        self.file.seek(0)
        return self

    def __next__(self):
        while True:
            #loop to skip comment or bank lines
            #get next line
            try:
                line = self.file.readline()
            except:
                raise IOError("Error reading UCD file: {}".format(self.fpath))
            if line == '':
                self.file.close()
                raise StopIteration

            try:
                #remove comments and any resulting whole blank lines
                line = line.split('\n')[0]
                line = line.split('#')[0]
                line = line.rstrip().lstrip()
                if line == '':
                    continue

                #extract semicolon delimited fields
                fields = line.split(';')
                #print('input line : ' + str(fields))
                res = {}
                #character range
                if self.spec[0][1] == 'CODERANGE':
                    charRange = fields[0].split('..')
                    res['first'] = int(charRange[0], base=16)
                    res['last'] = int(charRange[1], base=16) if len(charRange) > 1 else res['first']

                #other mappings
                for fieldSpec in self.spec:
                    if fieldSpec[0] < len(fields):
                        if fieldSpec[1] == 'NOPROCESS':
                            res[fieldSpec[0]] = fields[fieldSpec[0]]
                        else:
                            res[fieldSpec[1]] = fields[fieldSpec[0]].rstrip().lstrip().replace(' ', '_')

                return res
            except:
                raise ValueError("Error parsing UCD file: {}, at line: {}".format(self.fpath, line))


class UCDTestCases():
    '''
    provides tests from a ucd boundary test file

    Returns tuples: (pattern, test, line)
        target:     str representation of the test target
        test:       a list of allowed break positions,
                    first value before first character, last value after last character
        line:       the original test str, for error messages
    '''
    def __init__(self, name):
        self.ucd = UCDLineInput(name)

    def __iter__(self):
        self.ucd.__iter__()
        return self

    def __next__(self):
        line = self.ucd.__next__()
        fields = line[0].split()
        target = []
        test    = []
        for i, field in enumerate(fields):
            if i % 2 == 0:
                if (field == "\xc3\xb7") or (field == "\xf7"):
                    test.append(i // 2)
            else:
                target.append(chr(int(field, base=16)))
        target = ''.join(target)
        return target, test, line[0]


def compileEncoding(encoding):
    ''' Compile standard build of unicode property classes.

    Compiled classes are written to disk in subdirectoy of unicode environment

    Params:
        encoding    a string specifying a valid python codec

    Raises:
        does not raise - exits on logged error

    '''
    normEncoding = normaliseName(encoding)

    #build main build directory
    if not os.path.isdir(__compileRoot):
        #build if necessary
        try:
            os.makedirs(__compileRoot)
        except Exception as e:
            UCDLog.error('Failed to make UCD compile root directory {}, exception: {}'.format(__compileRoot, str(e)))
            exit(1)

    #encode directory
    encDir = os.path.join(__compileRoot, normEncoding)
    ''' DEBUG
    if not os.path.isdir(encDir):
        #build new directories
        try:
            os.makedirs(encDir)
        except Exception as e:
            UCDLog.error('Failed to make encoding directory {}, exception: {}'.format(encDir, str(e)))
            exit(1)
    else:
        #directory exists, delete files
        for f in os.listdir(encDir):
            fpath = os.path.join(encDir, f)
            try:
                if os.path.isfile(fpath):
                    os.unlink(fpath)
                else:
                    shutil.rmtree(fpath)
            except Exception as e:
                UCDLog.error('Failed to delete directory {} contents, exception: {}'.format(encDir, str(e)))
                exit(1)

    # compile files
    for name in BUILD_LIST:
        compileCharacterClasses(normEncoding, name)

    # build combined classes & other properties
    for spec in COMBINED_GENERAL:
        _buildCombinedCharacters(normEncoding, spec[0][0], spec[0][1], spec[1], spec[2], spec[3])

    # build special cases

    # script extensions
    _compileScriptExtensions(normEncoding)
    '''
    # any
    cc = getAny(normEncoding)
    pp = os.path.join(__compileRoot, normEncoding)
    _storeClass(pp, normEncoding, '', 'any', cc)
    # ascii
    cc.loadFromRange(0, 0x7F)
    _storeClass(pp, normEncoding, '', 'ascii', cc)
    # assigned
    '''
    props = getPropertyValueNames(None, 'Cn')
    cp = getClassPath(normEncoding, *props)
    if cp == None:
        # no unassigned characters in this encoding
        cc = CharClass(normEncoding)
    else:
        cc.loadFromFile(getClassPath(normEncoding, *props))
    cc.inverse()
    _storeClass(pp, normEncoding, '', 'assigned', cc)
    # dot_any - ie any without line breaks to simulate the standard '.' re
    cc = getAny(normEncoding)
    cr = CharClass(normEncoding)
    props = getPropertyValueNames(None, 'newline')
    cr.loadFromFile(getClassPath(normEncoding, *props))
    cc.difference(cr)
    _storeClass(pp, normEncoding, '', 'dot_any', cc)
    '''

def compileCharacterClasses(encoding, name):
    ''' Build all classes specified from a given build name and encoding.

    This reads named script files (see headers) from the UCD database, compiles
    resulting character classes with the given encoding and writes to file in
    subdirectory of the unicode database.

    Params:
        name         the internal build name, see BUILD_LIST in header
        encoding     a string specifying a valid python codec

    '''
    n_encoding   = normaliseName(encoding)
    ucd          = UCDLineInput(name)
    currScript   = ''
    charClass    = CharClass(n_encoding)
    scriptLoaded = False
    nSpace       = UCD_NAMESPACE[name]
    if nSpace == '':
        valDir   = __propertyNames
    else:
        valDir   = __propertyValues[nSpace]
    propPath     = os.path.join(__compileRoot, n_encoding)

    for ldir in ucd:
        if ldir['PropertyName'] != currScript:
            #new script section
            if scriptLoaded:
                #finish existing script, write to disk if characters present
                _storeClass(propPath, n_encoding, nSpace, valDir[currScript.lower()], charClass)
                charClass    = CharClass(n_encoding)
            currScript   = ldir['PropertyName']

        charClass.union(CharClass(n_encoding, ifirstChar=ldir['first'], ilastChar=ldir['last']))
        scriptLoaded = True

    #finish last script
    _storeClass(propPath, n_encoding, nSpace, valDir[currScript.lower()], charClass)


def _compileScriptExtensions(encoding):
    ''' Build compiled script extensions on disk for given encoding.

    Params:
        encoding:    normalised encoding name
    '''
    ucd        = UCDLineInput(SCRIPT_EXTENSION_NAME)
    propPath   = os.path.join(__compileRoot, encoding)
    propName   = UCD_NAMESPACE['script_extensions']
    extensions = {}

    # first load all extensions into separate character classes
    for ldir in ucd:
        newCodes = CharClass(encoding, ifirstChar=ldir['first'], ilastChar=ldir['last'])
        scripts  = ldir[1].rstrip().lstrip().split()
        for script in scripts:
            prop = getPropertyValueNames(None, script)
            if prop == None:
                raise SystemError("Script extension not in property namespace")
            if prop[1] not in extensions:
                extensions[prop[1]] = CharClass(encoding)
            extensions[prop[1]].union(newCodes.clone())

    # get all existing scripts for this encoding, add and save extensions to each
    for script in os.listdir(os.path.join(propPath, 'script')):
        scriptClass = CharClass(encoding)
        scriptClass.loadFromFile(os.path.join(propPath, 'script', script))
        if script in extensions:
            scriptClass.union(extensions[script])
        _storeClass(propPath, encoding, propName, script, scriptClass)


def _getCaseFolding():
    ''' Load case folding table from ucd database.
    '''
    ucd          = UCDLineInput('CaseFolding')
    cases        = {}
    for ldir in ucd:
        if ldir['type'] not in ['S', 'C']:
            continue
        try:
            mapping = chr(int(ldir['target'], base=16))
        except:
            continue
        source = chr(ldir['first'])
        # insert
        if mapping in cases:
            # if mapping already exists insert in the chain
            oldSource = cases[mapping]
            cases[mapping] = source
            cases[source]  = oldSource
        else:
            # build simple chain
            cases[mapping] = source
            cases[source]  = mapping
    return cases


def getCaseFolding():
    ''' Return pre-loaded case folding dictionary.

    Dictionary is a circular map from character to character.
    Each group of characters is either 2 or 3 long.
    '''
    return __cases


def _getAllSymbolAliases():
    ''' Build a dictionary of aliases for unicode symbols (eg character classes)

    The standard internal name (ie used in file names and processing generally)
    is the normal (database) long name form in lower case. The dictionary maps
    all name forms (including self, and ' ' '-' '_' variants) to this name.

    Result:
        propertyNames    dictionary of property name variants -> standard name
        propetryValues   dictionary of dictionaries
                         property ->{variant value name -> standard value name}
    '''
    ucd          = UCDLineInput('PropertyAliases')
    propertyNames = {}

    for ldir in ucd:
        standardName = normaliseName(ldir['long'])
        propertyNames[normaliseName(ldir['short'])] = standardName
        propertyNames[standardName]                 = standardName
        #add any alternative names
        for i in range(4):
            if i in ldir:
                propertyNames[normaliseName(ldir[i])] = standardName

    #add special names (Any, Assigned, ASCII ...)
    for p in UCD_EXTRA_PROPERTIES:
        standardName = normaliseName(p)
        propertyNames[standardName] = standardName

    ucd          = UCDLineInput('PropertyValueAliases')
    propertyValues = {}

    #build propertyValues: propertyName->{valueName->standardValueName)
    for ldir in ucd:
        p = normaliseName(ldir['property'])
        if p not in propertyNames:
            continue
        p = propertyNames[p]   # standard form for p
        if p not in propertyValues:
            propertyValues[p] = {}
        pdir = propertyValues[p]
        standardName = normaliseName(ldir['long'])
        pdir[normaliseName(ldir['short'])] = standardName
        pdir[standardName] = standardName
        #add any alternative names
        for i in range(4):
            if i in ldir:
                pdir[normaliseName(ldir[i])] = standardName

    # PATCH **********
    # at present the unicode database does not include scx value aliases, temporary equate to sc
    propertyValues['script_extensions'] = propertyValues['script']

    # add special values
    for p, v in UCD_EXTRA_VALUES:
        vname = normaliseName(v)
        pname = normaliseName(p)
        propertyValues[pname][vname] = vname

    return  propertyNames, propertyValues


def isEncodingInstalled(encoding):
    ''' Test if an encoding name is installed (ie pre-compiled)
    '''
    if normaliseName(encoding) in __installedEncodings:
        return True
    return False


def normaliseName(enc):
    ''' Returns standard formatted version of encoding.

    Returns input in lower case with spaces or hyphens as underscores
    '''
    if enc == None:
        return None
    return enc.lower().lstrip().rstrip().replace(' ', '_').replace('-', '_')


def getPropertyValueNames(pName, value):
    ''' Tests if a property=value pair is in loaded namespace

    if pName is None then the search order is used to check possible values
    returns tuple of (property,value) using normalised names

    Params:
        pName    a property name
        value    a property value, or None

    Returns:
        a property (name,value) pair in standard form if present, otherwise None
    '''
    vtest = normaliseName(value)
    if pName == None or pName == '':
        # check if value is a (binary) property
        if vtest in __propertyNames:
            return '', __propertyNames[vtest]
        # otherwise list properties to search
        testList = UCD_PROPERTY_SEARCH
    else:
        testList = [normaliseName(pName)]

    for prop in testList:
        if prop in __propertyNames:
            normProp = __propertyNames[prop]
            if vtest in __propertyValues[normProp]:
                return normProp, __propertyValues[normProp][vtest]
    #not found
    return None


def getClassPath(encoding, pName, vName):
    ''' Provides the file path for a given encoding and property.

    Expects property and value names in standard format.
    If the characterClass is not installed, it returns None
    '''

    charClassPath = os.path.join(__compileRoot, normaliseName(encoding), pName, vName)
    if os.path.isfile(charClassPath):
        return charClassPath
    return None


def _buildCombinedCharacters(encoding, prop, value, sourceList, nameList, invert):
    ''' Combine existing classes and characters into a new character class.

    if possible build a new character class by combining classes (sourceList)
    and/or single character names (nameList).
    If invert is true the set is the inverse of that produced from lists.
    '''
    normProp, normValue = getPropertyValueNames(prop, value)
    storePath = os.path.join(__compileRoot, encoding)

    sourcePaths = []
    for v in sourceList:
        p = getClassPath(encoding, *(getPropertyValueNames(normProp, v)))
        if p != None:
            sourcePaths.append(p)
        else:
            UCDLog.warning('Class required for character combination not found: ' + v)
    charClass = newClassFromList(encoding, sourcePaths)

    for v in nameList:
        charClass.union(newCasedCharacter(__cases, encoding, v, False))

    if invert:
        charClass.inverse()

    if not charClass.isEmpty():
        _storeClass(storePath, encoding, normProp, normValue, charClass)


def _storeClass(propPath, encoding, prop, value, cClass):
    if cClass.isEmpty():
        return
    if (value == None) or (value == ''):
        raise SystemError('A property value must always be present for storing compiled character classes')
    elif (prop == None) or (prop == ''):
        cClass.toFile(os.path.join(propPath, value))
        propRef = value
    else:
        cClass.toFile(os.path.join(propPath, prop, value))
        propRef = prop + ' -> ' + value
    compiledStateSize = cClass.stateSize
    cClass.publishToGraph()
    pubCount = cClass.getStateSize()
    UCDLog.info('Completed {} encoding of {}. \tnumber of states = {:d} (publish size ={:d})'.format(encoding, propRef, compiledStateSize, pubCount))

#get name spaces into module
__propertyNames, __propertyValues = _getAllSymbolAliases()
__cases                           = _getCaseFolding()
