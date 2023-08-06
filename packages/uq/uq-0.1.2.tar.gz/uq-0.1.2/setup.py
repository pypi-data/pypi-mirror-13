#!/usr/bin/env python
# coding: utf-8

import os
from setuptools import setup, find_packages

requirements = [
    'python-etcd >= 0.4.3',
    'pymemcache >= 1.3.5',
    'redis >= 2.10.5',
    'requests >= 2.9.1',
]

f = open(os.path.join(os.path.dirname(__file__), 'README.rst'))
long_description = f.read()
f.close()

exec(open('uq/version.py').read())

setup(
    name='uq',
    version=__version__,
    description='Python library for uq cluster',
    long_description=long_description,
    url='http://github.com/amyangfei/pyuq',
    author='Yang Fei',
    author_email='amyangfei@gmail.com',
    maintainer='Yang Fei',
    maintainer_email='amyangfei@gmail.com',
    keywords=['Uq', 'message queue'],
    license='MIT',
    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements,
    test_suite='nose.collector',
    tests_require=[
        'nose',
    ]
)
