#!/usr/bin/python
from setuptools import setup
import sys
from pyat import __version__

setup (name = 'pyat',
        version = __version__,
        install_requires = [
            'six',
        ],
	packages = [
            'pyat',
        ],
)
