#!/usr/bin/env python

import os
import sys
from setuptools import setup


def root_dir():
    rd = os.path.dirname(__file__)
    if rd:
        return rd
    return '.'

needs_pytest = set(['pytest', 'test']).intersection(sys.argv)
pytest_runner = ['pytest_runner'] if needs_pytest else []


setup_args = dict(
    name='cherrypy-dynpool',
    version='2.2',
    url='https://bitbucket.org/tabo/cherrypy-dynpool/',
    author='Gustavo Picon',
    author_email='tabo@tabo.pe',
    license='Apache License 2.0',
    py_modules=['cherrypy_dynpool'],
    description='A dynamic thread pool tool for CherryPy 3.',
    long_description=open(root_dir() + '/README').read(),
    install_requires=[
        "CherryPy>=3.2",
        "dynpool>=2.0,<3.0"
    ],
    setup_requires=[
        'pytest-runner',
    ],
    tests_require=[
        'pytest',
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries'])

if __name__ == '__main__':
    setup(**setup_args)
