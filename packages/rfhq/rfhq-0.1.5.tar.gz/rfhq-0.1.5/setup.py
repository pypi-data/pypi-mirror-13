# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import os
import codecs
import re
from setuptools import setup, find_packages

def read(*parts):
    filename = os.path.join(os.path.dirname(__file__), *parts)
    with codecs.open(filename, encoding='utf-8') as fp:
        return fp.read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(
        r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")

install_requires = [
    "Django>=1.8",
    "djangorestframework>=3",
    "inflection",
    "python-dateutil",
    "elasticsearch-dsl",
]

tests_require = [
    "nose",
    "pinocchio"
    "coverage",
    "mock",
]


setup(
    name='rfhq',
    version=find_version('rfhq', '__init__.py'),
    author='PredictHQ',
    long_description=read('README.rst'),
    install_requires=install_requires,
    test_suite='tests.runner.run_all',
    tests_require=tests_require,
    packages=find_packages(exclude=('tests*',)),
    include_package_data=True,
    license='MIT',
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Framework :: Django",
    ]
)
