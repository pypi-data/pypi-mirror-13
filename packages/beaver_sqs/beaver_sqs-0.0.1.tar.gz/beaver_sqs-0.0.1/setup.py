#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
del os.link

try:
    from setuptools import setup
    setup  # workaround for pyflakes issue #13
except ImportError:
    from distutils.core import setup

try:
    import multiprocessing
    multiprocessing
except ImportError:
    pass

from codecs import open

here = os.path.abspath(os.path.dirname(__file__))

# Get the long description from the README file
with open(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='beaver_sqs',
    version='0.0.1',
    author='Jamie Cressey',
    author_email='jamiecressey89@gmail.com',
    packages=[
        'beaver_sqs'
    ],
    url='http://github.com/python-beaver/beaver-sqs',
    license='LICENSE.txt',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: System :: Logging',
    ],
    description='python daemon that munches on logs and sends their contents to logstash',
    long_description=long_description,
    install_requires=['beaver', 'boto'],
    extras_require={
        'test': ['tox'],
    }
)
