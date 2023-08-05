#!/usr/bin/python3
# Copyright (c) 2015 Davide Gessa
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

from setuptools import find_packages
from setuptools import setup

setup(name='libcontractvm',
	version='0.6.9.4',
	description='Contractvm client library',
	author='Davide Gessa',
	setup_requires='setuptools',
	author_email='gessadavide@gmail.com',
	packages=['libcontractvm'],
	install_requires=open ('requirements.txt', 'r').read ().split ('\n')
)
