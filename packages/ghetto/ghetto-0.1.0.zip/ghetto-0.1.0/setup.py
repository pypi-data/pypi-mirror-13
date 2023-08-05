#!/usr/bin/env python

from setuptools import setup, find_packages
from os import path
import sys


PWD = path.abspath(path.dirname(__file__))
with open(path.join(PWD, 'README.md')) as f:
    LONG_DESC = f.read()

import ghetto

setup(
    name = 'ghetto',
    version = ghetto.VERSION,
    description = "A tool for (automatized) torrent files downloading from RSS feeds.",
    long_description = LONG_DESC,
    url = 'https://github.com/infinite-library/ghetto',
    author = 'Nikita K.',
    author_email = 'mendor@yuuzukiyo.net',
    license = 'MIT',
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: MIT License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2 :: Only',
        'Topic :: Utilities'
    ],
    keywords = 'ghetto torrent bittorrent rss',
    py_modules = ['ghetto'],
    entry_points = {
        'console_scripts': ['ghetto=ghetto:main']
    } 
)
