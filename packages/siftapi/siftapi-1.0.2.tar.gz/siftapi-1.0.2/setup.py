#!/usr/bin/env python
# coding=utf8

from setuptools import setup, find_packages

def readme():
    with open('README.rst') as f:
        return f.read()

setup(
    name='siftapi',
    version='1.0.2',

    description='A Python wrapper for EasilyDo\'s Sift API',
    long_description=readme(),

    url='http://sift.easilydo.com',

    author='EasilyDo',
    author_email='production@easilydo.com',
    license='MIT',

    keywords='email easilydo sift',

    packages=['siftapi'],

    install_requires=[
        'requests',
    ],
    test_suite='nose.collector',
    tests_require=['nose']
)

