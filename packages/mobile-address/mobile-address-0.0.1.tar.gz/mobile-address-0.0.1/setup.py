#!/usr/bin/env python
# coding=utf-8
# *************************************************
# File Name    : setup.py
# Author       : Cole Smith
# Mail         : tobewhatwewant@gmail.com
# Github       : whatwewant
# Created Time : 2016年02月12日 星期五 21时11分12秒
# *************************************************

import os
from setuptools import setup

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='mobile-address',
    version='0.0.1',
    packages=['mobile_address', ],
    # package_dir={'spherical_functions': '.'},
    include_package_data=True,
    install_requires = ['requests'],
    license='BSD License',
    description='A simple app for searching mobile address.',
    long_description=README,
    url='https://github.com/whatwewant/mobile-address',
    author='Cole Smith',
    author_email='tobewhatwewant@gmail.com',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
