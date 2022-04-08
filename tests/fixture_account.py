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

from unittest.mock import Mock
import pytest


@pytest.fixture
def account_describe_mock():
    mock = Mock()

    attributes = {
        'Account': {
            'Id': '345678901234',
            'Arn': 'arn:aws:some-arn',
            'Email': 'a@b.com',
            'Name': 'account-three',
            'Status': 'ACTIVE',
            'JoinedMethod': 'CREATED',
            'JoinedTimestamp': '20150101'
        }
    }
    mock.client.return_value.describe_account.return_value = attributes

    tags = {
        'Tags': [
            {
                'Key': 'account:holder',
                'Value': 'a@b.com'
            },

            {
                'Key': 'account:state',
                'Value': 'vanilla'
            }
        ]
    }
    mock.client.return_value.list_tags_for_resource.return_value = tags

    parents = {
        'Parents': [
            {
                'Id': 'ou-1234',
                'Type': 'ORGANIZATIONAL_UNIT'
            },
        ]
    }
    mock.client.return_value.list_parents.return_value = parents

    return mock
