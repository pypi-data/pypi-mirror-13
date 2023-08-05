# -*- coding: utf-8 -*-
 
 
"""setup.py: setuptools control."""
 
 
import re
from setuptools import setup
 
 
version = re.search(
    '^__version__\s*=\s*"(.*)"',
    open('demo/bootstrap.py').read(),
    re.M
    ).group(1)
 
 
with open("README.rst", "rb") as f:
    long_descr = f.read().decode("utf-8")
 
 
setup(
    name = "sectemp-bootstrap",
    packages = ["demo"],
    entry_points = {
        "console_scripts": ['bootstrap = demo.bootstrap:main']
        },
    version = version,
    description = "Python command line application bare bones template.",
    long_description = long_descr,
    author = "SP",
    author_email = "sp@wacko.com",
    url = "something",
    )