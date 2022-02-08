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

import json
import logging
from types import SimpleNamespace

import boto3

from code.event_bus import EventFactory


class Worker:

    @classmethod
    def prepare(cls, account, client=None):

        client = client if client else boto3.client('codebuild')  # allow code injection

        # client.create_project( ... )

        # client.start_build( ... )

        # to be moved to the end of the Codebuild buildspec
        EventFactory.emit('PreparedAccount', account)

    @classmethod
    def purge(cls, account, client=None):

        client = client if client else boto3.client('codebuild')  # allow code injection

        # client.create_project( ... )

        # client.start_build( ... )

        # to be moved to the end of the Codebuild buildspec
        EventFactory.emit('PurgedAccount', account)
