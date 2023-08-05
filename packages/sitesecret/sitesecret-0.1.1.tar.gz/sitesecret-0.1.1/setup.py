#!/usr/bin/env python
from setuptools import setup
import os
import re

VERSIONFILE = "sitesecret.py"


def get_version():
    with open(VERSIONFILE, 'rb') as f:
        return re.search("^__version__\s*=\s*['\"]([^'\"]*)['\"]",
                           f.read().decode('UTF-8'), re.M).group(1)


def read(*path):
    """
    Return content from ``path`` as a string
    """
    with open(os.path.join(os.path.dirname(__file__), *path), 'rb') as f:
        return f.read().decode('UTF-8')


setup(name='sitesecret',
      version=get_version(),
      description='Generate a per-site random secret',
      long_description=read('README.rst') + "\n\n" + read("CHANGELOG.rst"),
      py_modules=['sitesecret'],
      packages=[])
