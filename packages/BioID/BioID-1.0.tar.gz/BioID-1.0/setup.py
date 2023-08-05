#!/usr/bin/env python
# -*- coding: utf-8 -*-


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read().replace('.. :changelog:', '')

requirements = [
    'PyYAML',
    'binaryornot'
]

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='BioID',
    version='1.0',
    description="A python package for autonomously identifying Bioinformatic file formats.",
    long_description=readme + '\n\n' + history,
    author="Lee Bergstrand",
    url='https://github.com/LeeBergstrand/BioID',
    packages=[
        'BioID',
    ],
    package_dir={'BioID':
                 'BioID'},
    include_package_data=True,
    install_requires=requirements,
    license="MIT",
    zip_safe=True,
    keywords='BioID Bioinformatics ',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
		'Programming Language :: Python :: Implementation :: PyPy',
		'Operating System :: OS Independent',
		'Topic :: Scientific/Engineering :: Bio-Informatics'
    ],
    test_suite='tests',
    tests_require=test_requirements
)
