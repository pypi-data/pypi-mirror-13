#!/usr/bin/env python
# -*- coding: utf-8 -*-
import codecs
import re
import sys
from os import path

from setuptools import find_packages, setup

AUTHOR = 'Eirik Martiniussen Sylliaas'
DESCRIPTION = 'Abakus Status Checks'
EMAIL = 'eirik@sylliaas.no'
GIT = 'git@github.com:eirsyl/abakus-status-checks.git'
KEYWORDS = 'Monitoring, Status Checks, Abakus'
LICENSE = 'MIT'


try:
    from semantic_release import setup_hook
    setup_hook(sys.argv)
except ImportError:
    pass


def read(*parts):
    file_path = path.join(path.dirname(__file__), *parts)
    return codecs.open(file_path, encoding='utf-8').read()

version = re.search(
    r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
    read('abakus_checks/__init__.py'),
    re.MULTILINE
).group(1)

readme = open('README.rst').read()

setup(
    name='abakus-status-checks',
    version=version,
    description=DESCRIPTION,
    long_description=readme,
    author=AUTHOR,
    author_email=EMAIL,
    url=GIT,
    packages=find_packages(exclude='tests'),
    include_package_data=True,
    install_requires=read('requirements.txt').strip().split('\n'),
    license=LICENSE,
    zip_safe=False,
    keywords=KEYWORDS,
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
    ],
    tests_require=read('requirements-test.txt').strip().split('\n'),
    entry_points={
        'console_scripts': ['abakus-checks = abakus_checks.cli:cli']
    },
    extras_require={
    },
)
