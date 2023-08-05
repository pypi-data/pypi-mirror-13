#!/usr/bin/env python
from setuptools import setup
import os
import sys
import tempfile

setup(
    name='pip-spark',
    version='0.1',
    description='Graphing on the command line, from Holman',
    license='MIT',
    url='https://github.com/holman/spark',
    long_description='https://github.com/holman/spark',
    scripts=['spark'],
)
