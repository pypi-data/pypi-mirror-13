#!/usr/bin/env python

from setuptools import setup, find_packages


with open('VERSION.txt', 'r') as v:
    version = v.read().strip()

setup(
    name='yolodb',
    description='A simple key/whatever storage DB',
    author='gdraynz',
    author_email='gd.raynz@gmail.com',
    version=version,
    packages=find_packages(exclude=['tests']),
    license='WTFPL',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)
