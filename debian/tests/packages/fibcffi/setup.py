#!/usr/bin/env python

from setuptools import setup

setup(
    name='fibcffi',
    version='42.0.0',
    description='CFFI Fibonacci',
    py_modules=['fibcffi'],
    cffi_modules=['fibcffi_build.py:ffibuilder'],
    zip_safe=True,
)
