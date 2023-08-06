#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""CSL data setup."""
from __future__ import unicode_literals

import sys

from setuptools import setup

name = str('csl_data')

PY2 = sys.version_info[0] == 2

dependencies = [
    'json-document',
]
dependency_links = []

if not PY2:
    dependency_links.append(
        'git+https://github.com/zyga/json-document.git#egg=json-document',
    )

setup(
    name=name,
    version='0.1.1',
    description='CSL data structure.',
    keywords='csl json schema publication article journal',
    author='John Vandenberg',
    author_email='jayvdb@gmail.com',
    url='https://github.com/jayvdb/csl-data',
    install_requires=dependencies,
    dependency_links=dependency_links,
    tests_require=['unittest2'],
    test_suite='unittest2.collector',
    license='MIT',
    packages=[name],
    package_data={name: ['*.json']},
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Build Tools',
    ],
)
