#!/usr/bin/env python

import os
import sys
import io

from setuptools import setup, find_packages
from setuptools.command.install import install as _install

with io.open('README.rst') as f:
    readme = f.read()

REQUIRES = ['werkzeug', 'six', 'ipaddress', 'pathlib']

setup(
    name='urly',
    version='0.1.1455780396',
    description='Nice URLs for Python',
    long_description=readme,
    author='Robert Lechte',
    author_email='robertlechte@gmail.com',
    install_requires=REQUIRES,
    packages=find_packages(),
    classifiers=[
        'Development Status :: 3 - Alpha'
    ]
)
