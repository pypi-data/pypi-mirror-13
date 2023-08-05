embedc: Python Embedded C
Version 1.0
http://pyembedc.sourceforge.net
1/16/2016

Copyright 2010-2016 by Fernando Trias
See Artistic License in LICENSE

embedc enables Python source code to embed C/C++ snippets that seamlessly access and modify Python variables and call Python functions. 

PREREQUISITES

* GCC version 3 or higher
* Python 2.5 or higher (also compatible with Python 3)

INSTALL

    python setup.py install
    
TEST

You don't have to install before running the test:

    python test.py
    
The "test-coverage" script uses multiple python versions (2.5, 2.6, 3.1) and python-coverage to ensure most source lines are covered by the test suite.

This module has been tested on:

* Windows Vista with Cygwin Python 2.5 and GCC (mixed results, see Notes)
* Windows Vista with official Python 2.5 and 2.6 and MinGW
* Ubuntu (Debian Linux 2.6 kernel), Python 2.5, 2.6 and 3.1 and gcc 4.4.1

SAMPLE CODE
-------------------------------------------------

See web site, test.py and sample.py for examples and usage.

Simple example:

    from embedc import C
    v = [5,6,7]
    vlen = len(v)
    vsum = 0;
    r = C("for(int i=0;i<vlen;i++) vsum += v[i]")
    print vsum

USAGE
-------------------------------------------------
The embedc module provides all the functionality to embed C/C++ code, modify variables and call functions.

To use the library, first you must import it:
    from embedc import C

Functions:
--------------
C(string)
inline_c(string)
inline_c_precompile(string)
--------------

These will compile the "string" containing the C/C++ code and then link dynamically and run the code.

"string" is C/C++ code that can be used within a function. It can contain any valid C/C++ expression that your compiler will support. 

The "C" function will automatically provide references to all local Python variables for use in your code to read or write as if they were basic types or arrays.

The "inline_c" and "inline_c_precompile" fucntion will not provide references to local Python variables and thus is faster and consumes less memory. 

"inline_c_precompile" will compile the code only once to increase speed. The code must be given using the Python multi-line string format using three quotes '"""'. This is because the module will scan the source file and pick out the string. As a consequence, variable substitutions and other string operations will not work. For example, the following code will not work:
    C("""
    v=%s
    """) % (var1)

"string" must be valid C/C++ suitable for placment within a function. In addition, the code supports the following commands. Commands must be the first non-whitespace character in a line.

C/C++ COMMANDS
--------------

IMPORT type [&]variable

This will allow access to a Python variable within the code. Usually, this is not required for local variables because they are imported automatically. But in the case of the function "inline_c_precompile" this is not the case, and you must import all variables using IMPORT. In the case of global or class variables, you must use IMPORT.

"type" is any valid C type, such as "int", "double", "int[]". In addition, "string" is used to access strings, which C will treat as a "const char *".

"type" can also be an array if the Python type is a tuple, list or array. In this case add "[]" to the end of the type, in the manner of C/C++. For example, in Python "a=(1,5,3)", the IMPORT line would be "IMPORT int[] a".

"variable" is the Python variable to import. Normally, variables are imported by value, meaning that any changes in the C/C++ code are lost. However, if you add a "&" in front (the C/C++ symbol for reference), then the variables are imported by reference and any changes will be saved to the Python variables when the code finishes execution.

DEF return-type function [type1] [type2] [type3]...

Allow access to a Python function within the C/C++ code. "return-type" is any C/C++ type. At this time, only basic types are allowed. Arrays are not allowed. To return arrays, modify local variables. "type1", "type2", etc. are the data types of parameters. For example, the python function "def add2(num1, num2)" would be declared with "DEF int add2 int int". Then the C/C++ snipet would be "int x = add(5,3);".

GLOBAL code

Places the code in the global space. Usually, this is used to create a C/C++ global variable. These variables are available in the C/C++ code between calls to "C" or "inline_c_precomiple". This is is necessary because all the C/C++ code is placed within a function.

RETURN type value

Return a non-int value. Usually, return values for "C" or "inline_c_precompile" are of type "int". If "return" is not specified in the C/C++ code, then "return 0" is assumed. To return a different value, add a different "return" statement. If you want to return a different type rather than "int", then use RETURN and specify the type. For example, "RETURN double 1.7" will return a value of type "double" equal to 1.7.

POST code

Run code after executing the C/C++ snipet, writing back all the variables and the return value. Sometimes this is necessary wen your function needs to do some cleanup, such as when it allocates memory to return a string.

--------------
embed_c(string)
embed_c_precompile(string)
--------------
These functions are used to compile code but not execute then immediately. They return a CDLL object that can be executed using _call_function().


-------------------------------------------------
SPECIAL CONSIDERATIONS
-------------------------------------------------
When using embed_c_precompile and inline_c_precompile, embedc will read in the source file before it is interpreted. It will look for the function name and the triple-quote """ sequence. It will also look for another triple-quote """ to end. The close parenthesis must be on the same line as the ending triple-quote """ (see examples above). This is because embedc uses line numbers to find the precompiled function at run time.

-------------------------------------------------
TODO
-------------------------------------------------
* Allow additional compilers; allow passing GCC command line options.

* Support arrays of strings.

* Support returning strings from Python functions called from within C/C++ (modifying string variables is supported).

* With non-precompiled code, keep a cache of the source code so if it doesn't change it, we can just reuse the DLL/so.

-------------------------------------------------
REFERENCES AND NOTES
-------------------------------------------------
embedc makes heavy use of ctypes.

There are several alternatives to embedc. All of them have their pros and cons. Here are several:

PyInline <http://pyinline.sourceforge.net/> is a module for inlining multiple languages in Python last updated in 2001 that predates ctypes. It seeks to copy Perl Inline <http://search.cpan.org/~sisyphus/Inline-0.45/C/C.pod>.

ezpyinline <http://pypi.python.org/pypi/ezpyinline/0.1> is a fork of PyInline that provides a very simple interface for embedding C/C++ functions.

Neither PyInline nor ezpyinline hande arrays. I think C provides the greatest speed advantage when looping over large amounts of data and performing multiple calculations. Without arrays or the ability to return more than one number (PyInline and ezpyinline provide only one return value), that advantage is hard to realize. embedc fixes these shortcoming by using ctypes to allow C/C++ to access and modify arrays.

These modules also don't provide an easy mechanism for accessing and altering Python variables from within the C/C++ code. With them, to modify variables from C, you have to code in the Python API, which is neither easy nor straightforward. 

In addition, they require a working python development environment. This can be complex on Linux if you are not using standard packages, and is also difficult in Windows. By using ctypes, embedc does not require a working Python build environment, thus simplifying deployment because there is no need to configure include paths, lib paths and so forth. The only requirement is a working compiler.

PyRex <http://wiki.python.org/moin/Pyrex> is a Python-like language that mixes C and Python to create Python modules. This is a very interesting approach, but isn't really Python and requires a great deal of expertise to use.

-------------------------------------------------
KNOWN ISSUES:
-------------------------------------------------

Cygwin:
    Cygwin has numerous problems with the test script because it quickly runs out of resources. The test script covers too many scenarios loading too many different DLLs for Cygwin to handle.

    If you get an error like this on Windows:
        *** fatal error - unable to remap tmpE9X11V.cpp.dll to same address as parent(0x2B0000) != 0x3B0000
        python 5368 fork: child 1676 - died waiting for dll loading, errno 11
    Check out http://inamidst.com/eph/cygwin for a possible solution.

    Occasionally, this error might come up in the test.py script:
        OSError: [Errno 11] Resource temporarily unavailable
    This is due to the limitations of Cygwin.
    
Local Variables: Modifying local variables is tricky and required embedc to call internal Python API functions. It has been tested on Python 2.5, 2.6, and 3.1 but may break in future versions if the internal representation of frames and variables changes.
