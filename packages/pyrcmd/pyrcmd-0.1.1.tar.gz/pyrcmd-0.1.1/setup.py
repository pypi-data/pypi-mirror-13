#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#
from os.path import dirname, join
from setuptools import setup, find_packages

# requirements
with open('requirements.txt') as f:
    required = f.read().splitlines()

with open(join(dirname(__file__), 'pyrcmd/VERSION'), 'rb') as f:
    version = f.read().decode('ascii').strip()

setup(
    name="pyrcmd",
    version=version,
    description="Python Remote Commands toolkit",
    long_description=open('README.rst').read(),
    author="Marreta",
    author_email="coder@marreta.org",
    maintainer="Bruno Costa, Kairo Araujo",
    maintainer_email="coder@marreta.org",
    url="https://github.com/marreta/pyrcmd/",
    keywords="Python Remote Command Commands SSH Toolkit",
    packages=find_packages(exclude=['*.test', 'tests.*']),
    package_data={'': ['license.txt', 'pyrcmd/VERSION']},
    install_requires=required,
    include_package_data=True,
    license='BSD',
    platforms='Posix; MacOS X; Windows',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: Unix',
        'Topic :: System :: Shells',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)
