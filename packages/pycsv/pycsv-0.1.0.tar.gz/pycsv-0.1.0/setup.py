#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='pycsv',
    version='0.1.0',
    url='https://www.github.com/azime/pycsv/',
    author='Abderrahim AZIME',
    author_email='azime_1@yahoo.fr',
    description='Simple module for reading csv file',
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    test_suite = 'nose.collector',
    #setup_requires=[
    #    'nose==1.3.3',
    #],
)