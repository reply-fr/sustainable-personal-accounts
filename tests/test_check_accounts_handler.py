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

import json
from unittest.mock import patch, Mock
import os

from code.check_accounts_handler import handle_event, validate_tags

import pytest
# pytestmark = pytest.mark.wip


@patch.dict(os.environ, dict(ORGANIZATIONAL_UNITS_PARAMETER="SomeParameter",
                             VERBOSITY='DEBUG'))
def test_handle_event():

    mock = Mock()

    chunk = {
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
            },

            {
                'Id': '345678901234',
                'Arn': 'arn:aws:some-arn',
                'Email': 'string',
                'Name': 'account-three',
                'Status': 'ACTIVE',
                'JoinedMethod': 'CREATED',
                'JoinedTimestamp': '20150101'
            },
        ]
    }
    mock.client.return_value.list_accounts_for_parent.return_value = chunk

    get_parameter = {'Parameter': {'Value': json.dumps({'hello': 'world'})}}
    mock.client.return_value.get_parameter.return_value = get_parameter

    describe_account = {'Account': {'Arn': 'arn:aws', 'Email': 'a@b.com', 'Name': 'name', 'Status': 'ACTIVE'}}
    mock.client.return_value.describe_account.return_value = describe_account

    list_tags_for_resource = {'Tags': {}}
    mock.client.return_value.list_tags_for_resource.return_value = list_tags_for_resource

    list_parents = {'Parents': [{'Id': 'ou-1234'}]}
    mock.client.return_value.list_parents.return_value = list_parents

    result = handle_event(event=dict(hello='world!'), context=None, session=mock)
    assert result == '[OK]'


def test_validate_tags():
    valid_tags = {'account:holder': 'a@b.com',
                  'account:state': 'released'}
    validate_tags(account='123456789012', tags=valid_tags)


def test_validate_tags_on_absent_holder():
    absent_holder = {'account:state': 'released'}
    with pytest.raises(ValueError):
        validate_tags(account='123456789012', tags=absent_holder)


def test_validate_tags_on_invalid_holder():
    invalid_holder = {'account:holder': 'a_b.com',
                      'account:state': 'released'}
    with pytest.raises(ValueError):
        validate_tags(account='123456789012', tags=invalid_holder)


def test_validate_tags_on_absent_state():
    absent_state = {'account:holder': 'a@b.com'}
    with pytest.raises(ValueError):
        validate_tags(account='123456789012', tags=absent_state)


def test_validate_tags_on_invalid_state():
    invalid_state = {'account:holder': 'a@b.com',
                     'account:state': '*alien*'}
    with pytest.raises(ValueError):
        validate_tags(account='123456789012', tags=invalid_state)
