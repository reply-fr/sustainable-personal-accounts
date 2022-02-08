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

import boto3


class Accounts:

    @staticmethod
    def list(parent, client=None):
        client = client if client else boto3.client('organizations')

        token = None
        while True:
            logging.info(f"listing accounts in parent '{parent}'")
            parameters = dict(ParentId=parent,
                              MaxResults=50)
            if token:
                parameters['NextToken'] = token
            chunk = client.list_accounts_for_parent(**parameters)

            for item in chunk['Accounts']:
                logging.info(json.dumps(item))
                yield item['Id']

            token = chunk.get('NextToken')
            if not token:
                break
