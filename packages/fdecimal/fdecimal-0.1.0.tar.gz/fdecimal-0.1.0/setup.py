#!/usr/bin/env python
# -*- coding: utf-8 -*-


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import fdecimal


with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read().replace('.. :changelog:', '')


setup(
    name='fdecimal',
    version='0.1.0',
    description="Decimal compatability with float",
    long_description=readme + '\n\n' + history,
    author="Ben Lopatin",
    author_email='ben@benlopatin.com',
    url='https://github.com/bennylope/fdecimal',
    packages=[
        'fdecimal',
    ],
    package_dir={'fdecimal':
                 'fdecimal'},
    include_package_data=True,
    license="BSD",
    zip_safe=False,
    keywords='fdecimal',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        #'Programming Language :: Python :: 3',
        #'Programming Language :: Python :: 3.4',
    ],
    test_suite='tests',
)
