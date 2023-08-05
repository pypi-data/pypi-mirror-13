import codecs
import os
import sys
 
try:
    from setuptools import setup
except:
    from xlutils3 import setup

def read(fname):

    return codecs.open(os.path.join(os.path.dirname(__file__), fname)).read()
 
NAME = "xlutils3"
 
PACKAGES = ["xlutils3",]
 
DESCRIPTION = "this is a test package for packing python liberaries tutorial.It is based on xlutils1.7 and can be used in python3.4+ programs."

LONG_DESCRIPTION = read("README.txt")
 
KEYWORDS = "python python3 xlutils xlrd xlwt"
 
AUTHOR = "slqt"
 
AUTHOR_EMAIL = "hzqt210@gmail.com"
 
URL = "https://github.com/slqt/python_xlutils_approve.git"
 
VERSION = "1.0.2"

LICENSE = "GPL"

setup(
    name = NAME,
    version = VERSION,
    description = DESCRIPTION,
    long_description = LONG_DESCRIPTION,
    classifiers = [
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
    ],
    keywords = KEYWORDS,
    author = AUTHOR,
    author_email = AUTHOR_EMAIL,
    url = URL,
    license = LICENSE,
    packages = PACKAGES,
    include_package_data=True,
    zip_safe=True,
)
