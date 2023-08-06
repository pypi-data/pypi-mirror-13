#!/usr/bin/env python

from distutils.core import setup

import uuid64


def readme():
    try:
        with open('README.rst') as f:
            return f.read()
    except:
        return '(Could not read from README.rst)'


setup(name='temporaluuid64',
      py_modules=['uuid64'],
      version=uuid64.__version__,
      description='A time-based 64-bit UUID generator',
      long_description=readme(),
      author=uuid64.__author__,
      author_email=uuid64.__email__,
      url='http://github.com/suminb/temporaluuid64',
      packages=[],
      )
