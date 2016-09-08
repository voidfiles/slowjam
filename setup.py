#!/usr/bin/env python

import os
import re
import sys

from codecs import open

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

        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

packages = [
    'slowjam',
    'slowjam.ext',
    'slowjam.ext.django',
]

requires = []
test_requirements = ['pytest>=2.8.0']

with open('slowjam/__init__.py', 'r') as fd:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                        fd.read(), re.MULTILINE).group(1)

if not version:
    raise RuntimeError('Cannot find version information')

with open('README.rst', 'r', 'utf-8') as f:
    readme = f.read()


setup(
    name='slowjam',
    version=version,
    description='Python Application Tracer',
    long_description=readme,
    author='Bryan Berg, Mark Thurman, Alex Kessinger',
    url='https://github.com/voidfiles/slowjam',
    packages=packages,
    package_data={'': ['LICENSE']},
    package_dir={'slowjam': 'slowjam'},
    include_package_data=True,
    install_requires=requires,
    license='MIT',
    zip_safe=False,
    classifiers=(
        'Development Status :: 5 - Production/Stable',
    ),
    cmdclass={'test': PyTest},
    tests_require=test_requirements
)
