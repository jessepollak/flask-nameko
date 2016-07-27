#!/usr/bin/env python
# -*- coding: utf-8 -*-


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


with open('README.md') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    # TODO: put package requirements here
    #
    # These requirements should be pinned according to SemVer.
    # i.e.
    # "left_pad>=1.0, <2.0"
]

test_requirements = [
    # TODO: put package test requirements here
    "mock==2.0.0",
    "pytest"
]

setup(
    name='flask-nameko',
    version='0.1.0',
    description="A wrapper for using nameko services with Flask",
    long_description=readme + '\n\n' + history,
    author="Jesse Pollak",
    author_email='jesse@getclef.com',
    url='https://github.com/clef/flask-nameko',
    packages=[
        'flask-nameko',
    ],
    package_dir={'flask-nameko':
                 'flask-nameko'},
    include_package_data=True,
    install_requires=requirements,
    license="ISCL",
    zip_safe=False,
    keywords='flask-nameko',
    classifiers=['Private :: Do Not Upload'],
    test_suite='tests',
    tests_require=test_requirements,
    setup_requires=['pytest-runner']
)
