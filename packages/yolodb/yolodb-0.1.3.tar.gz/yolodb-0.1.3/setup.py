#!/usr/bin/env python

from pip.req import parse_requirements
from setuptools import setup, find_packages


with open('VERSION.txt', 'r') as v:
    version = v.read().strip()

# Requirements
install_reqs = parse_requirements('requirements.txt', session='dummy')
reqs = [str(ir.req) for ir in install_reqs]

setup(
    name='yolodb',
    url='https://github.com/gdraynz/yolodb',
    description='A simple key/whatever storage DB',
    author='gdraynz',
    author_email='gd.raynz@gmail.com',
    version=version,
    install_requires=reqs,
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
