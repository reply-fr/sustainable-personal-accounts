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
from moto import mock_organizations, mock_ssm
import os
import pytest
from types import SimpleNamespace

from lambdas import Account, State

# pytestmark = pytest.mark.wip
from tests.fixture_small_setup import given_a_small_setup


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


@pytest.mark.unit_tests
@patch.dict(os.environ, dict(TAG_PREFIX='hello:'))
def test_get_tag_key():
    result = Account.get_tag_key(suffix='world')
    assert result == 'hello:world'
    result = Account.get_tag_key(suffix='universe')
    assert result == 'hello:universe'


@pytest.mark.integration_tests
def test_enumerate_tags(valid_tags):
    iterator = Account.enumerate_tags(account='123456789012',
                                      session=valid_tags)
    assert next(iterator) == {'Key': 'account-holder', 'Value': 'a@b.com'}
    assert next(iterator) == {'Key': 'account-state', 'Value': 'vanilla'}
    assert next(iterator) == {"Key": "another_tag", "Value": "another_value"}
    with pytest.raises(StopIteration):
        next(iterator)


@pytest.mark.unit_tests
def test_set_state_to_vanilla():
    session = Mock()
    Account.set_state(account='0123456789012',
                      state=State.VANILLA,
                      session=session)
    session.client.assert_called_with('organizations')
    session.client.return_value.tag_resource.assert_called_with(
        ResourceId='0123456789012',
        Tags=[{'Key': 'account-state', 'Value': 'vanilla'}])


@pytest.mark.unit_tests
def test_set_state_to_assigned():
    session = Mock()
    Account.set_state(account='0123456789012',
                      state=State.ASSIGNED,
                      session=session)
    session.client.assert_called_with('organizations')
    session.client.return_value.tag_resource.assert_called_with(
        ResourceId='0123456789012',
        Tags=[{'Key': 'account-state', 'Value': 'assigned'}])


@pytest.mark.unit_tests
def test_set_state_to_released():
    session = Mock()
    Account.set_state(account='0123456789012',
                      state=State.RELEASED,
                      session=session)
    session.client.assert_called_with('organizations')
    session.client.return_value.tag_resource.assert_called_with(
        ResourceId='0123456789012',
        Tags=[{'Key': 'account-state', 'Value': 'released'}])


@pytest.mark.unit_tests
def test_set_state_to_expired():
    session = Mock()
    Account.set_state(account='0123456789012',
                      state=State.EXPIRED,
                      session=session)
    session.client.assert_called_with('organizations')
    session.client.return_value.tag_resource.assert_called_with(
        ResourceId='0123456789012',
        Tags=[{'Key': 'account-state', 'Value': 'expired'}])


@pytest.mark.unit_tests
def test_set_state_raises_exception():
    with pytest.raises(ValueError):
        Account.set_state(account='0123456789012',
                          state=SimpleNamespace(value='*something*'))


@pytest.mark.integration_tests
@mock_organizations
@mock_ssm
def test_untag():
    context = given_a_small_setup()
    Account.untag(account=context.alice_account, keys=['account-holder'])


@pytest.mark.integration_tests
@mock_organizations
@mock_ssm
def test_list():
    context = given_a_small_setup()
    result = {x for x in Account.list(parent=context.committed_ou)}
    assert result == {context.crm_account, context.erp_account}


@pytest.mark.integration_tests
@mock_organizations
@mock_ssm
def test_describe():
    context = given_a_small_setup()
    item = Account.describe(id=context.alice_account)
    assert len(item.id) == 12
    assert item.arn.startswith('arn:aws:organizations::')
    assert item.email == 'alice@example.com'
    assert item.name == 'alice'
    assert item.is_active
    assert item.tags.get('account-holder') == 'alice@example.com'
    assert item.tags.get('account-state') == 'released'
    assert item.unit == context.sandbox_ou
    item = Account.describe(id=context.bob_account)
    assert len(item.id) == 12
    assert item.arn.startswith('arn:aws:organizations::')
    assert item.email == 'bob@example.com'
    assert item.name == 'bob'
    assert item.is_active
    assert item.tags.get('account-holder') == 'bob@example.com'
    assert item.tags.get('account-state') == 'expired'
    assert item.unit == context.sandbox_ou


@pytest.mark.integration_tests
@mock_organizations
@mock_ssm
def test_get_name():
    context = given_a_small_setup()
    assert Account.get_name(account=context.root_account) == "Example Corporation"
    assert Account.get_name(account=context.alice_account) == "alice"


@pytest.mark.integration_tests
@mock_organizations
@mock_ssm
def test_get_organizational_unit():
    context = given_a_small_setup()
    assert Account.get_organizational_unit(account=context.root_account).startswith('r-')
    assert Account.get_organizational_unit(account=context.alice_account) == context.sandbox_ou


@pytest.mark.integration_tests
@mock_organizations
@mock_ssm
def test_get_organizational_unit_name():
    context = given_a_small_setup()
    assert Account.get_organizational_unit_name(account=context.root_account) == 'Root'
    assert Account.get_organizational_unit_name(account=context.alice_account) == context.sandbox_ou_name


@pytest.mark.unit_tests
def test_validate_holder():
    Account.validate_holder('alpha-nc.aws.cloudops.fr@example.com')


@pytest.mark.unit_tests
def test_get_cost_management_tag():

    with patch.dict(os.environ, dict(COST_MANAGEMENT_TAG='cost-center')):
        assert Account.get_cost_management_tag() == 'cost-center'

    with patch.dict(os.environ, dict(COST_MANAGEMENT_TAG='')):
        assert Account.get_cost_management_tag() == 'cost-center'

    with patch.dict(os.environ, dict(COST_MANAGEMENT_TAG='customTag')):
        assert Account.get_cost_management_tag() == 'customTag'


@pytest.mark.unit_tests
def test_get_cost_center():

    defaultTag = {'cost-center': 'standard BU'}
    customTag = {'customTag': 'customised BU'}

    with patch.dict(os.environ, dict(COST_MANAGEMENT_TAG='cost-center')):
        assert Account.get_cost_center(tags=defaultTag) == 'standard BU'
        assert Account.get_cost_center(tags=customTag) == 'NoCostTag'

    with patch.dict(os.environ, dict(COST_MANAGEMENT_TAG='')):
        assert Account.get_cost_center(tags=defaultTag) == 'standard BU'
        assert Account.get_cost_center(tags=customTag) == 'NoCostTag'

    with patch.dict(os.environ, dict(COST_MANAGEMENT_TAG='customTag')):
        assert Account.get_cost_center(tags=defaultTag) == 'NoCostTag'
        assert Account.get_cost_center(tags=customTag) == 'customised BU'
