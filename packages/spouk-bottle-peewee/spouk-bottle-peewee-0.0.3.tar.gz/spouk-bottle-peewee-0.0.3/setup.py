#!/usr/bin/env python

import sys
import os
from distutils.core import setup

try:
    from distutils.command.build_py import build_py_2to3 as build_py
except ImportError:
    from distutils.command.build_py import build_py

setup(
    name = 'spouk-bottle-peewee',
    version = '0.0.3',
    url = 'http://spouk.ru',
    description = 'orm peewee integrating plugin for bottle',
    long_description = """
    https://github.com/DevSpouk/spouk_bottle_peewee

    """,
    author = 'Spouk',
    author_email = 'spouk@spouk.ru',
    license = 'MIT',
    platforms = 'any',
    py_modules = [
        'spouk_bottle_peewee'
    ],
    requires = [
        'bottle (>=0.9)',
        'peewee (>=2.6.3)',
    ],
    classifiers = [
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    cmdclass = {'build_py': build_py}
)
