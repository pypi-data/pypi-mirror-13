#!/usr/bin/env python
#coding:utf-8
"""
  Author:   --<>
  Purpose: 
  Created: 2015/12/28
"""

import codecs
import os
import sys

try:
    from setuptools import setup
except:
    from distutils.core import setup
def read(fname):
    return codecs.open(os.path.join(os.path.dirname(__file__), fname)).read()
NAME = "lpp"
PACKAGES = ["lpp",]
DESCRIPTION = " A function package for bioinfomatics"

LONG_DESCRIPTION = read("README.rst")
KEYWORDS = "mulit dimension hash, bioinfomatics,lpp"
AUTHOR = "Pengpeng Li"
AUTHOR_EMAIL = "409511038@qq.com"
VERSION = "1.0.2"

setup(
    name = NAME,
    version = VERSION,
    description = DESCRIPTION,
    long_description = LONG_DESCRIPTION,
    classifiers = [
        
        'Programming Language :: Python',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
		'Programming Language :: Python :: 2',
    ],
	url="https://github.com/lpp1985/lpp_Script",
    install_requires=[
        "requests",
        "pandas",
        "pdb",
        "numpy"
        ],    
    keywords = KEYWORDS,
    author = AUTHOR,
    author_email = AUTHOR_EMAIL,

    packages = PACKAGES,
    include_package_data=True,
    zip_safe=True,
)
 
