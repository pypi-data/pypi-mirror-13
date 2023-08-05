#!/usr/bin/env python

from setuptools import setup, find_packages
import pycsv

setup(
    name='pycsv',
    version=pycsv.__version__,
    url='https://www.github.com/azime/pycsv/',
    author='Abderrahim AZIME',
    author_email='azime_1@yahoo.fr',
    description='Simple module for reading csv file',
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    test_suite = 'nose.collector',
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7"
    ]
)