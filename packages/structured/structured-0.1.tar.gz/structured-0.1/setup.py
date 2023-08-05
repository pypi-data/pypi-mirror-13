#!/usr/bin/env python

import sys
import os

try:
    from setuptools import setup
    setup
except ImportError:
    from distutils.core import setup

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

VERSION = "0.1"

setup(
    name="structured",
    version=VERSION,
    description="Query Lang to extract data from structures",
    author="Maksym Klymyshyn",
    author_email="klymyshyn@gmail.com",
    url="https://github.com/joymax/",
    packages=["structured"],
    long_description=open("README.rst").read(),
    include_package_data=True,
    install_requires=["nose",],
    test_suite="nose",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
    ]
)
