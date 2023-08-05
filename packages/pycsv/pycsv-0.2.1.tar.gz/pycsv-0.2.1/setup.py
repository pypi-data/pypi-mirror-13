#!/usr/bin/env python

from setuptools import setup, find_packages
import pycsv
import io

setup(
    name='pycsv',
    version=pycsv.__version__,
    url='https://www.github.com/azime/pycsv/',
    author='Abderrahim AZIME',
    author_email='azime_1@yahoo.fr',
    description='Simple module for reading csv file',
    long_description=io.open("history.md", encoding='utf8').read(),
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    test_suite = 'nose.collector',
    classifiers=[
        "Programming Language :: Python :: 2.7"
    ]
)
