'''
Setup file for jsre regular expressions

@author: Howard Chivers

Copyright (c) 2015, Howard Chivers
All rights reserved.
'''

from setuptools import setup, Extension
from os import path, listdir

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.rst')) as f:
    long_description = f.read()


def getRefFiles(base, root):
    rf = []
    for f in listdir(path.join(base, root)):
        p = path.join(root, f)
        if path.isdir(path.join(base, p)):
            rf.extend(getRefFiles(base, p))
        else:
            rf.append(p)
    return rf

jsremod  = path.join(here, 'jsre')
refFiles = getRefFiles(jsremod, 'UnicodeDatabase')
refFiles.extend(getRefFiles(jsremod, 'JSRE_Compiled'))
refFiles.extend(getRefFiles(jsremod, 'JSRE_Test'))
refFiles.extend(getRefFiles(jsremod, 'docs'))

jsvm_mod = Extension('jsvm', sources=['jsvm/jsvm.c', 'jsvm/jsvm_core.c'])

setup(

    name='jsre',

    version='1.0.0',

    description='Regular expression module for forensics and big data',
    long_description=long_description,

    author='Howard Chivers',
    author_email='howard.chivers@york.ac.uk',

    license='BSD New',

    classifiers=['Development Status :: 4 - Beta',
                 'Intended Audience :: Science/Research',
                 'License :: OSI Approved :: BSD License',
                 'Operating System :: OS Independent',
                 'Programming Language :: Python :: 3',
                 'Topic :: Scientific/Engineering :: Information Analysis',
                 'Topic :: Software Development :: Libraries :: Python Modules',
                 'Topic :: Text Processing :: General',
                 ],

    keywords='regular expressions search forensic',

    packages=['jsre', 'jsvm'],
    package_dir={'jsre': 'jsre', 'jsvm': 'jsvm'},

    ext_modules=[jsvm_mod],

    scripts=['jsre/tools.py'],

    package_data={'jsre': refFiles, 'jsvm': ['jsvm.h']}
)
