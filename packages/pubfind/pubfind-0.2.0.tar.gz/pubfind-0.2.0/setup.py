#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""pubfind setup."""
from __future__ import unicode_literals

import sys

from setuptools import setup, find_packages

name=str('pubfind')

dependencies = [
    'csl_data',
    'ConfigArgParse',
    'requests',
]

if sys.version_info[0] == 2:
    dependencies.append('unicodecsv')

setup(
    name=name,
    version='0.2.0',
    description='Publication search command line tool.',
    keywords='csl scopus csv json schema publication article journal',
    author='John Vandenberg',
    author_email='jayvdb@gmail.com',
    url='https://github.com/jayvdb/pubfind',
    license='MIT',
    packages=[name],
    install_requires=dependencies,
    entry_points={
        'console_scripts': [name + ' = ' + name + '.cmd:main'],
    },
    package_data={name: ['*.json']},
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
    ],
)
