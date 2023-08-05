#!/usr/bin/env python
# coding: utf-8
import os
import platform
import sys

from setuptools import setup
from setuptools.command.test import test as TestCommand


class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass into py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest

        sys.path.insert(0, os.path.dirname(__file__))

        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


requirements = []
test_requirements = ['pytest>=2.8.0']


if sys.version_info[:2] == (3, 2):
    test_requirements.append('coverage==3.7.1')

if not platform.system() == 'Java':
    test_requirements.append('pytest-cov==1.8')


setup(
    name='simple-money',
    version='0.1.2',
    author='Dmitry Dygalo',
    author_email='dadygalo@gmail.com',
    maintainer='Dmitry Dygalo',
    maintainer_email='dadygalo@gmail.com',
    description='A simple interface to work with money-related entities.',
    license='MIT',
    keywords=['money', 'finance'],
    url='https://github.com/Stranger6667/simple-money',
    packages=['simple_money', 'tests'],
    long_description='',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Topic :: Office/Business :: Financial',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Programming Language :: Python :: Implementation :: Jython',
    ],
    install_requires=requirements,
    tests_require=test_requirements,
    cmdclass={'test': PyTest}
)
