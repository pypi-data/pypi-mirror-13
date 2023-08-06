#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

dependencies = []

setup(
    name='leryan.types',
    version='0.0.2',
    packages=find_packages(exclude=['tests.*']),
    author='Florent Peterschmitt',
    author_email='florent@peterschmitt.fr',
    install_requires=dependencies,
    description='some "types": classes derived from python dict, list...',
    include_package_data=False,
    url='https://github.com/Leryan/leryan.types',
    license='BSD',
    classifiers=[
        'Programming Language :: Python :: 2.7'
    ],
    test_suite='leryan',
)
