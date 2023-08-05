#!/usr/bin/env python
# coding: UTF-8

from setuptools import setup
from fy import __description__, __author__, __version__
import os
import shutil

if not os.path.exists('scripts'):
    os.makedirs('scripts')
shutil.copyfile('fy.py', 'scripts/fy')

with open("README.rst", "r") as f:
    readme_file = f.read()

setup(
    name="fixYabinary",
    version=__version__,
    author=__author__,
    author_email="i.am.tkmru@gmail.com",
    py_modules=['fy', 'signature'],
    scripts=['scripts/fy'],
    url="https://github.com/tkmru/fixYabinary",
    license="MIT License",
    keywords=["binary", "ctf"],
    description=__description__,
    long_description=readme_file,
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License"
        ]
)
