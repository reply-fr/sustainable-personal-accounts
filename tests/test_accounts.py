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

import logging
logging.getLogger('botocore').setLevel(logging.CRITICAL)
logging.getLogger('urllib3').setLevel(logging.CRITICAL)

import pytest

from code import Accounts

pytestmark = pytest.mark.wip


class BotoMock:

    def list_accounts_for_parent(self, *args, **kwargs):

        if not kwargs.get('NextToken'):
            return {
                'Accounts': [
                    {
                        'Id': '123456789012',
                        'Arn': 'arn:aws:some-arn',
                        'Email': 'string',
                        'Name': 'account-one',
                        'Status': 'ACTIVE',
                        'JoinedMethod': 'CREATED',
                        'JoinedTimestamp': '20150101'
                    },

                    {
                        'Id': '234567890123',
                        'Arn': 'arn:aws:some-arn',
                        'Email': 'string',
                        'Name': 'account-two',
                        'Status': 'ACTIVE',
                        'JoinedMethod': 'CREATED',
                        'JoinedTimestamp': '20150101'
                    }
                ],
                'NextToken': 'token'
            }

        else:
            return {
                'Accounts': [
                    {
                        'Id': '345678901234',
                        'Arn': 'arn:aws:some-arn',
                        'Email': 'string',
                        'Name': 'account-three',
                        'Status': 'ACTIVE',
                        'JoinedMethod': 'CREATED',
                        'JoinedTimestamp': '20150101'
                    }
                ]
            }


def test_list():
    iterator = Accounts.list(parent='ou-parent',
                             client=BotoMock())
    assert next(iterator) == '123456789012'
    assert next(iterator) == '234567890123'
    assert next(iterator) == '345678901234'
    with pytest.raises(StopIteration):
        next(iterator)
