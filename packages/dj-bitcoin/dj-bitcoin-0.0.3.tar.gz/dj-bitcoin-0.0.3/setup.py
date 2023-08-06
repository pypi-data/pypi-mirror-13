#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import re

from setuptools import setup


def get_version(package):
    """
    Return package version as listed in `__version__` in `init.py`.
    """
    init_py = open(os.path.join(package, '__init__.py')).read()
    return re.search("__version__ = ['\"]([^'\"]+)['\"]", init_py).group(1)


version = get_version('djbitcoin')
readme = open('README.rst').read()

setup(
    name='dj-bitcoin',
    version=version,
    url='https://github.com/silverlogic/dj-bitcoin',
    license='MIT',
    description='Django helpers for working with bitcoin',
    long_description=readme,
    author='Ryan Pineo',
    author_email='ryanpineo@gmail.com',
    packages=['djbitcoin'],
    install_requires=[],
    zip_safe=False,
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Internet :: WWW/HTTP',
    ]
)
