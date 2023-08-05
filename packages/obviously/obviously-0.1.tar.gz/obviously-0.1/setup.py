#!/usr/bin/env python

from distutils.core import setup
from setuptools import find_packages
import os


def get_readme():
    if os.path.isfile("README.txt"):
        filename = "README.txt"
    else:
        filename = "README.rst"
    with open(filename, 'r') as f:
        return f.read()

setup(
    name="obviously",
    version='0.1',
    description="Rspec-style test helper, but with more attitude.",
    long_description='``obviously.the()`` to wrap an object, then describe its behavior with the available methods.',
    author="Haak Saxberg",
    author_email="haak.erling@gmail.com",
    url="http://github.com/haaksmash/obviously",
    packages=find_packages(),
)
