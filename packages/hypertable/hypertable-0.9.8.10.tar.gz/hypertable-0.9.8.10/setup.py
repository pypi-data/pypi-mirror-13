# -*- coding: utf-8 -*-
import os
from setuptools import setup, find_packages

README_RST = os.path.join(os.path.dirname(__file__), 'README.rst')
with open(README_RST) as readme:
    long_description = readme.read()

setup(
    name='hypertable',
    version='0.9.8.10',
    description='Python client for Hypertable',
    long_description=long_description,

    packages=find_packages(exclude=['gen-py.*', 'gen-py']),
    scripts=['client_test.py'],
    install_requires=['thrift>=0.9.3'],

    url='http://hypertable.com/documentation/developer_guide/python/',
    license='GPLv3',
)
