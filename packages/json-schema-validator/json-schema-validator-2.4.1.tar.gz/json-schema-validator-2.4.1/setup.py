#!/usr/bin/env python
#
# Copyright (C) 2010, 2011 Linaro Limited
# Copyright (C) 2014, Canonical Ltd.
#
# Author: Zygmunt Krynicki <zygmunt.krynicki@linaro.org>
#
# This file is part of json-schema-validator.
#
# json-schema-validator is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License version 3
# as published by the Free Software Foundation
#
# json-schema-validator is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with json-schema-validator.  If not, see <http://www.gnu.org/licenses/>.

import sys

from setuptools import setup, find_packages

test_dependencies = [
    'testscenarios >= 0.1',
    'testtools >= 0.9.2'
]

if sys.version_info[0] == 2:
    test_dependencies.append('PyYaml')

setup(
    name='json-schema-validator',
    version=":versiontools:json_schema_validator:__version__",
    author="Zygmunt Krynicki",
    author_email="me@zygoon.pl",
    description="JSON Schema Validator",
    packages=find_packages(),
    url='https://github.com/zyga/json-schema-validator',
    test_suite='json_schema_validator.tests.test_suite',
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        ("License :: OSI Approved :: GNU Library or Lesser General Public"
         " License (LGPL)"),
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
    ],
    setup_requires=[
        'versiontools >= 1.3.1'],
    tests_require=test_dependencies,
    zip_safe=True)
