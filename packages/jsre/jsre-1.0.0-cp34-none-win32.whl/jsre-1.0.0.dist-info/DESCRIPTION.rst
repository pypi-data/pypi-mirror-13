============
Introduction
============

This module provides a regular expression matching engine optimised for searching large 
byte buffers, for example large files or raw disk images, using multiple 
encodings. Typical applications include big data extraction tasks including artefact 
discovery for digital forensics.

jsre is:

*   **Fast:** When matching complex patterns or a large number of keywords on large
    input buffers it is substantially faster than current regular expression
    engines. jsre is designed to scale well in the face of complexity: its 
    relative performance improves with increasing pattern complexity.
*   **Unicode Encoding Neutral:** A regular expression is written as a string,
    the user separately specifies what encodings are to be searched when the
    expression is compiled. All Python codecs are supported and the capability 
    provided is compilant with Unicode regular expression level 1 requirements.
*   **Deployable:** The compiled matching engine has a small memory
    footprint limited to below 10MByte, allowing processing to be easily 
    distributed across multiple CPUs.
*   **Portable:** The software uses a single Python type extension and only
    standard C and Python libraries. Installs with ``pip`` on Windows or Linux.

jsre includes additional functions that are specific to its intended
application, they include alternative expression indexing, the processing of overlapped
buffers and the specification of stride and offset for search anchors
(e.g. for searching at fixed positions in disk sectors).

To achieve execution efficiency and relative compactness jsre trades compiler
performance. Do not expect the compilation process to be fast, especially if the
pattern to be matched involves large number of code points and encodings that 
are capable of representing the full Unicode code range. This should
not be a controlling factor for the performance of this module against its intended
application.

As far as possible jsre provides a similar interface to the standard Python
re module. See documentation examples for an introduction to the module
and its application-specific features. This documentation assumes that the reader
is familiar with regular expressions and their use; newcomers may find it
easier to first read the Python re documentation and tutorials.

Contact: howard.chivers@york.ac.uk



