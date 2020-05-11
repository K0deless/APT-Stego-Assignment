#!/usr/bin/python3
#-*- use: utf-8 -*-
'''
Python tool to hide information inside of text through a key.

File: setup.py

@authors:
    - David Regueira
    - Santiago Rocha
    - Eduardo Blazquez
    - Jorge Sanchez
'''

import sys
from kagenokotoba import __version__

from setuptools import setup, find_packages

if sys.version_info < (3, 5):
    print("Unsupported python version, install Python 3.5 or greater", file=sys.stderr)
    sys.exit(1)

with open('requirements.txt','r') as fp:
    install_requires = fp.read().splitlines()

setup(
    name='kage no kotoba',
    description='Steganography tool to hide messages within a text finally to images',
    long_description="""Kage No Kotoba (or in Kanji 影の言葉) is a tool aimed
    to hide information from an input file using an intermediate cover text
    extracted from a semi-random url, the process of hiding the file in the
    text generate a key that is hidden in a image file that can be sent from
    the source to destination going unnoticed.
    """,
    version=__version__,
    packages=find_packages(),
    install_requires=install_requires,
    setup_requires=['setuptools'],
    python_requires='>=3.5',
    classifiers=[
                 'Programming Language :: Python',
                 'Programming Language :: Python :: 3',
                 'Programming Language :: Python :: 3.5',
                 'Programming Language :: Python :: 3.6',
                 'Programming Language :: Python :: 3.7',
                 'Programming Language :: Python :: 3.8',
                 'Programming Language :: Python :: 3 :: Only',
                 'Topic :: Steganography',
                 'Topic :: Security'
    ]
)