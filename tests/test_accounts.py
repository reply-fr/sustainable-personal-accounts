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

from unittest.mock import Mock
import pytest

from code import Accounts

pytestmark = pytest.mark.wip


def test_list():

    chunk_1 = {
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

    chunk_2 = {
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

    mock = Mock()
    mock.client.return_value.list_accounts_for_parent.side_effect = [chunk_1, chunk_2]
    iterator = Accounts.list(parent='ou-parent',
                             session=mock)
    assert next(iterator) == '123456789012'
    assert next(iterator) == '234567890123'
    assert next(iterator) == '345678901234'
    with pytest.raises(StopIteration):
        next(iterator)
