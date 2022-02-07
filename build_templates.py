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

import os
import logging

from aws_cdk import App

from code import Configuration, FunctionsStack


def build_templates(settings=None, dry_run=False):
    ''' generate CloudFormation templates '''

    Configuration.initialize(stream=settings, dry_run=dry_run)

    app = App()
    FunctionsStack(app, "functions-stack")
    app.synth()


if __name__ == '__main__':
    verbosity = logging.__dict__.get(os.environ.get('VERBOSITY'), 'INFO')
    logging.basicConfig(format='%(message)s', level=verbosity)
    logging.getLogger('botocore').setLevel(logging.CRITICAL)
    build_templates()
