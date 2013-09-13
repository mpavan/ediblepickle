#!/usr/bin/env python

import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

settings = dict()

# Publish Helper.
if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

CLASSIFIERS = [
    'Intended Audience :: Developers',
    'Natural Language :: English',
    'License :: OSI Approved :: Apache Software License',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
    'Topic :: Utilities',
]

settings.update(
    name='ediblepickle',
    version='1.1.3',
    description='Checkpoint',
    long_description=open('README.rst').read(),
    author='Pavan Mallapragada',
    license='Apache 2.0',
    url='https://github.com/mpavan/ediblepickle',
    classifiers=CLASSIFIERS,
    keywords="decorator, checkpoint, intermediate results, serialization, deserialization",
    py_modules=['ediblepickle'],
    tests_require=["nose"],
    test_suite="checkpoint_tests",
)


setup(**settings)
