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
    "nameko",
    "flask"
]

test_requirements = [
    # TODO: put package test requirements here
    "mock==2.0.0",
    "pytest"
]

setup(
    name='flask_nameko',
    version='1.0.1',
    description="A wrapper for using nameko services with Flask",
    long_description=readme + '\n\n' + history,
    author="Jesse Pollak",
    author_email='jesse@getclef.com',
    url='https://github.com/clef/flask_nameko',
    packages=[
        'flask_nameko',
    ],
    package_dir={'flask_nameko':
                 'flask_nameko'},
    include_package_data=True,
    install_requires=requirements,
    license="ISCL",
    zip_safe=False,
    keywords='flask_nameko',
    classifiers=[],
    test_suite='tests',
    tests_require=test_requirements,
    setup_requires=['pytest-runner']
)
