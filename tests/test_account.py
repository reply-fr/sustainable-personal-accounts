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

from unittest.mock import Mock, patch
import os
import pytest
from types import SimpleNamespace

from code import Account, State

# pytestmark = pytest.mark.wip


@pytest.fixture
def valid_tags():

    chunk_1 = {
        'Tags': [
            {
                'Key': 'account-holder',
                'Value': 'a@b.com'
            },

            {
                'Key': 'account-state',
                'Value': 'vanilla'
            }
        ],
        'NextToken': 'token'
    }

    chunk_2 = {
        'Tags': [
            {
                'Key': 'another_tag',
                'Value': 'another_value'
            }
        ]
    }

    mock = Mock()
    mock.client.return_value.list_tags_for_resource.side_effect = [chunk_1, chunk_2]
    return mock


@pytest.mark.integration_tests
def test_list_tags(valid_tags):
    tags = Account.list_tags(account='123456789012',
                             session=valid_tags)
    assert tags == {'account-holder': 'a@b.com', 'account-state': 'vanilla', 'another_tag': 'another_value'}


@patch.dict(os.environ, dict(TAG_PREFIX='hello:'))
@pytest.mark.unit_tests
def test_get_tag_key():
    result = Account.get_tag_key(suffix='world')
    assert result == 'hello:world'
    result = Account.get_tag_key(suffix='universe')
    assert result == 'hello:universe'


@pytest.mark.integration_tests
def test_iterate_tags(valid_tags):
    iterator = Account.iterate_tags(account='123456789012',
                                    session=valid_tags)
    assert next(iterator) == {'Key': 'account-holder', 'Value': 'a@b.com'}
    assert next(iterator) == {'Key': 'account-state', 'Value': 'vanilla'}
    assert next(iterator) == {"Key": "another_tag", "Value": "another_value"}
    with pytest.raises(StopIteration):
        next(iterator)


@pytest.mark.unit_tests
def test_move_to_vanilla():
    session = Mock()
    Account.move(account='0123456789012',
                 state=State.VANILLA,
                 session=session)
    session.client.assert_called_with('organizations')
    session.client.return_value.tag_resource.assert_called_with(
        ResourceId='0123456789012',
        Tags=[{'Key': 'account-state', 'Value': 'vanilla'}])


@pytest.mark.unit_tests
def test_move_to_assigned():
    session = Mock()
    Account.move(account='0123456789012',
                 state=State.ASSIGNED,
                 session=session)
    session.client.assert_called_with('organizations')
    session.client.return_value.tag_resource.assert_called_with(
        ResourceId='0123456789012',
        Tags=[{'Key': 'account-state', 'Value': 'assigned'}])


@pytest.mark.unit_tests
def test_move_to_released():
    session = Mock()
    Account.move(account='0123456789012',
                 state=State.RELEASED,
                 session=session)
    session.client.assert_called_with('organizations')
    session.client.return_value.tag_resource.assert_called_with(
        ResourceId='0123456789012',
        Tags=[{'Key': 'account-state', 'Value': 'released'}])


@pytest.mark.unit_tests
def test_move_to_expired():
    session = Mock()
    Account.move(account='0123456789012',
                 state=State.EXPIRED,
                 session=session)
    session.client.assert_called_with('organizations')
    session.client.return_value.tag_resource.assert_called_with(
        ResourceId='0123456789012',
        Tags=[{'Key': 'account-state', 'Value': 'expired'}])


@pytest.mark.unit_tests
def test_move_with_exception():
    with pytest.raises(ValueError):
        Account.move(account='0123456789012',
                     state=SimpleNamespace(value='*something*'))


@pytest.mark.unit_tests
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
    iterator = Account.list(parent='ou-parent',
                            session=mock)
    assert next(iterator) == '123456789012'
    assert next(iterator) == '234567890123'
    assert next(iterator) == '345678901234'
    with pytest.raises(StopIteration):
        next(iterator)


def test_describe(account_describe_mock):

    item = Account.describe(id='123456789012',
                            session=account_describe_mock)
    assert item.id == '123456789012'
    assert item.arn == 'arn:aws:some-arn'
    assert item.email == 'a@b.com'
    assert item.name == 'account-three'
    assert item.is_active
    assert item.tags.get('account-holder') == 'a@b.com'
    assert item.tags.get('account-state') == 'vanilla'
    assert item.unit == 'ou-1234'


def test_get_session():
    assert Account.get_session() is not None


@pytest.mark.unit_tests
def test_validate_holder():
    Account.validate_holder('alpha-nc.aws.cloudops.fr@acme.com')
