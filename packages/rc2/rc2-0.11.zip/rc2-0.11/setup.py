#!/usr/bin/env python

# Use setuptools, if available.  Otherwise, fall back to distutils.
try:
    from setuptools import setup
except ImportError:
    import sys
    sys.stderr.write("warning: Proceeding without setuptools\n")
    from distutils.core import setup

setup(
    name='rc2',
    py_modules=["rc2"],
    version='0.11',
    test_suite='test',
    description="RC2 (Rivest's Cipher version 2) Cipher",
    author='koha',
    author_email='kkoha@msn.com',
    url='http://kkoha.tistory.com/entry/Python-RC2',
    keywords = "RC2,ARC2,crypto,symmetric-key block cipher,Ron Rivest,Ron's Code,Rivest Cipher,64-bit block cipher",
    classifiers=[
        'Programming Language :: Python :: 2.7',
        'Topic :: Security :: Cryptography',
    ],
    long_description="""\

This module implements the RC2 (Rivest's Cipher version 2) encryption algorithm in pure python, specified in RFC 2268.

ECB and CBC modes are supported.

Original source code : https://github.com/0xEBFE/RC2-python/blob/master/rc2.py

Backorting Python 3 Code to Python 2.7.x by koha <kkoha@msn.com>

""")
