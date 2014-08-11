#!/usr/bin/env python

import re
import codecs
import os

try:
    pass
except ImportError:
    pass


from setuptools import setup


def read(*parts):
    return codecs.open(os.path.join(os.path.dirname(__file__), *parts)).read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError('Unable to find version string.')


def find_install_requires():
    return [x.strip() for x in
            read('requirements.txt').splitlines()
            if x.strip() and not x.startswith('#')]


def find_tests_require():
    return [x.strip() for x in
            read('test-requirements.txt').splitlines()
            if x.strip() and not x.startswith('#')]


README = read('README.md')

setup(
    name='ontimer',
    entry_points={
        'console_scripts': ['ontimer = ontimer.app:main',
                            'boss = ontimer.boss:main']
    },
    version=find_version('ontimer', '__init__.py'),
    url='https://github.com/walnutgeek/OnTimer',
    author='Walnut Geek',
    author_email='wg@walnutgeek.com',
    description="OnTimer - running stuff on time.",
    long_description=README,
    packages=['ontimer', 'ontimer.tests'],
    include_package_data=True,
    install_requires=find_install_requires(),
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: Apache Public License 2.0',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    test_suite='ontimer.tests',
    tests_require=find_tests_require(),
)
