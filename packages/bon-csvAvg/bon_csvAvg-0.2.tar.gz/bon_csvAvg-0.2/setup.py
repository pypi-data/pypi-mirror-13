#!/usr/bin/env python3

from setuptools import setup

setup(
    name = 'bon_csvAvg',
    version = '0.2',
    description = 'calculate the average of a number of bonnie++ test',
    long_description = open('README.rst', 'r').read(),
    platforms = ['any'],
    keywords = 'bonnie',
    author = 'Jayme',
    author_email = 'tuxnet@gmail.com',
    url = 'https://github.com/jayme-github/bon_csvAvg',
    license = 'GNU Affero General Public License v3',
    classifiers = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
    ],
    scripts = ['bon_csvAvg.py'],
)
