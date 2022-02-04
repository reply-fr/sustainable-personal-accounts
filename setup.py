#!/usr/bin/env python3
"""
Copyright Reply.com or its affiliates. All Rights Reserved.
SPDX-License-Identifier: Apache-2.0
Permission is hereby granted, free of charge, to any person obtaining a copy of this
software and associated documentation files (the "Software"), to deal in the Software
without restriction, including without limitation the rights to use, copy, modify,
merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import setuptools


with open("README.md") as fp:
    long_description = fp.read()


setuptools.setup(
    name="sustainable_personal_accounts",
    version="0.0.1",

    description="a set of cloud resources suited to manage thousands of AWS accounts assigned to individual innovators",
    long_description=long_description,
    long_description_content_type="text/markdown",

    author="Bernard Paques",

    package_dir={"": "code"},
    packages=setuptools.find_packages(where="code"),

    install_requires=[
        "aws-cdk-lib>=2.0.0rc1",
        "constructs>=10.0.0",
        "boto3",
        "pyyaml",
        "requests",
    ],

    python_requires=">=3.7",

    classifiers=[  # as per https://pypi.org/classifiers/
        "Development Status :: 3 - Alpha",

        "Framework :: AWS CDK",
        "Framework :: Flake8",
        "Framework :: Pytest",

        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",

        "License :: OSI Approved :: Apache Software License",

        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.7",

        "Topic :: Internet",
        "Topic :: Scientific/Engineering",
        "Topic :: Security",
        "Topic :: Software Development",
        "Topic :: System :: Installation/Setup",
        "Topic :: System :: Systems Administration",
        "Topic :: Utilities",

    ],
)
