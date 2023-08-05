# -*- coding: utf-8 -*-
from setuptools import setup


VERSION = (0, 0, 1)
__version__ = VERSION
__versionstr__ = '.'.join(map(str, VERSION))

packages = [
    "reflex",
]

setup(
    name = 'reflex-client',
    description = "Reflex Python client",
    url = "https://github.com/immunda/reflex-py",
    version = __versionstr__,
    author = "Phil Howell",
    author_email = "phil@quae.co.uk",
    packages = packages,
    classifiers = [
        "Development Status :: 1 - Planning",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
    ],
)