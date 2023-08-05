#!/usr/bin/python3
#-*- coding:utf-8 -*-

from setuptools import setup
import Unit
import os

old_readme = open("README.md", "r")
with open("README.rst", "w") as f:
    f.write(old_readme.read())

long_desc = """
Quickly chain functions together and write 
easier, functional solutions.
"""

conf = {
    	"name"             :"Unit.py",
	"version"          : Unit.__version__,
        "description"      : Unit.__description__,
        "long_description" : long_desc,
        "url"              : Unit.__url__,
        "author"           : Unit.__author__,
        "author_email"     : Unit.__email__,
        "license"          : Unit.__license__,
        "classifiers":[
            "Development Status :: 5 - Production/Stable",
            "Intended Audience :: Developers",
            "Programming Language :: Python :: 2",
            "Programming Language :: Python :: 2.6",
            "Programming Language :: Python :: 2.7",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.2",
            "Programming Language :: Python :: 3.3",
            "Programming Language :: Python :: 3.4",
            ],
        "keywords":"functor unit functions nesting comprehension",
        "packages":["Unit"],
        "install_requires":[],
        "extras_require":{},
        "package_data":{},
}
setup(**conf)

# Clean old file
os.remove("README.rst")
# end
