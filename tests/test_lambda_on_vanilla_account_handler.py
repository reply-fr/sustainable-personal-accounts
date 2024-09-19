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
from moto import mock_aws
import os
import pytest

from lambdas import Events, State
from lambdas.on_vanilla_account_handler import handle_organization_event, handle_tag_event

# pytestmark = pytest.mark.wip


@pytest.fixture
def valid_tags():

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
    mock.client.return_value.list_tags_for_resource.side_effect = [chunk_1, chunk_2]

    parameter = json.dumps({'ou-1234': {'budget_cost': 500.0}, 'ou-5678': {'budget_cost': 300}})
    mock.client.return_value.get_parameter.return_value = dict(Parameter=dict(Value=parameter))

    mock.client.return_value.list_parents.return_value = dict(Parents=[dict(Id='ou-1234')])

    return mock


@pytest.mark.integration_tests
@patch.dict(os.environ, dict(ACCOUNTS_PARAMETER="Accounts",
                             AWS_REGION='eu-west-1',
                             ENVIRONMENT_IDENTIFIER="envt1",
                             ORGANIZATIONAL_UNITS_PARAMETER="OrganizationalUnits",
                             VERBOSITY='DEBUG'))
@mock_aws
def test_handle_organization_event(valid_tags, given_a_small_setup):
    context = given_a_small_setup()
    event = Events.load_event_from_template(template="fixtures/events/move-account-template.json",
                                            context=dict(account=context.bob_account,
                                                         destination_organizational_unit=context.sandbox_ou,
                                                         origin_organizational_unit=context.unmanaged_ou))
    result = handle_organization_event(event=event, context=None, session=valid_tags)
    assert result['Source'] == 'SustainablePersonalAccounts'
    assert result['DetailType'] == 'CreatedAccount'
    details = json.loads(result['Detail'])
    assert details['Environment'] == 'envt1'
    assert details['Account'] == context.bob_account
    assert details.get('Message') is None


@pytest.mark.integration_tests
@patch.dict(os.environ, dict(ACCOUNTS_PARAMETER="Accounts",
                             AWS_REGION='eu-west-1',
                             ENVIRONMENT_IDENTIFIER="envt1",
                             ORGANIZATIONAL_UNITS_PARAMETER="OrganizationalUnits",
                             VERBOSITY='DEBUG'))
@mock_aws
def test_handle_tag_event(valid_tags, given_a_small_setup):
    context = given_a_small_setup()
    event = Events.load_event_from_template(template="fixtures/events/tag-account-template.json",
                                            context=dict(account=context.bob_account,
                                                         new_state=State.VANILLA.value))
    result = handle_tag_event(event=event, context=None, session=valid_tags)
    assert result['Source'] == 'SustainablePersonalAccounts'
    assert result['DetailType'] == 'CreatedAccount'
    details = json.loads(result['Detail'])
    assert details['Environment'] == 'envt1'
    assert details['Account'] == context.bob_account
    assert details.get('Message') is None


@pytest.mark.integration_tests
@patch.dict(os.environ, dict(ACCOUNTS_PARAMETER="Accounts",
                             ORGANIZATIONAL_UNITS_PARAMETER="OrganizationalUnits",
                             VERBOSITY='INFO'))
def test_handle_tag_event_on_unexpected_event(valid_tags):
    event = Events.load_event_from_template(template="fixtures/events/tag-account-template.json",
                                            context=dict(account="123456789012",
                                                         new_state=State.ASSIGNED.value))
    result = handle_tag_event(event=event, context=None, session=valid_tags)
    assert result == "[DEBUG] Unexpected state 'assigned' for this function"
