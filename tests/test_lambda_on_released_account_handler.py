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
from unittest.mock import Mock, patch
from moto import mock_aws
import os
import pytest

from lambdas import Events, State
from lambdas.on_released_account_handler import handle_tag_event

# pytestmark = pytest.mark.wip


@pytest.fixture
def session():
    mock = Mock()
    mock.client.return_value.create_policy.return_value = dict(Policy=dict(Arn='arn:aws'))
    mock.client.return_value.create_project.return_value = dict(project=dict(arn='arn:aws'))
    mock.client.return_value.get_parameter.return_value = dict(Parameter=dict(Value='buildspec_content'))
    mock.client.return_value.get_role.return_value = dict(Role=dict(Arn='arn:aws'))
    mock.client.return_value.describe_account.return_value = dict(Account=dict(Arn='arn:aws',
                                                                               Email='a@b.com',
                                                                               Name='Some-Account',
                                                                               Status='ACTIVE'))

    parents = {
        'Parents': [
            {
                'Id': 'ou-1234',
                'Type': 'ORGANIZATIONAL_UNIT'
            },
        ]
    }
    mock.client.return_value.list_parents.return_value = parents

    parameter_1 = dict(Parameter=dict(Value=json.dumps({'ou-1234': {'budget_cost': 500.0}, 'ou-5678': {'budget_cost': 300}})))
    parameter_2 = dict(Parameter=dict(Value=json.dumps({'ou-1234': {'budget_cost': 500.0}, 'ou-5678': {'budget_cost': 300}})))
    parameter_3 = dict(Parameter=dict(Value='buildspec_content'))
    mock.client.return_value.get_parameter.side_effect = [parameter_1, parameter_2, parameter_3]

    tags = {
        'Tags': [
            {
                'Key': 'account-holder',
                'Value': 'a@b.com'
            },

            {
                'Key': 'account-state',
                'Value': 'vanilla'
            }
        ]
    }
    mock.client.return_value.list_tags_for_resource.return_value = tags

    return mock


@pytest.mark.integration_tests
@patch.dict(os.environ, dict(ACCOUNTS_PARAMETER="Accounts",
                             AWS_DEFAULT_REGION='eu-west-1',
                             ENVIRONMENT_IDENTIFIER="envt1",
                             EVENT_BUS_ARN='arn:aws',
                             ORGANIZATIONAL_UNITS_PARAMETER="OrganizationalUnits",
                             PREPARATION_BUILDSPEC_PARAMETER="parameter-name",
                             VERBOSITY='DEBUG'))
@mock_aws
def test_handle_tag_event(session):
    event = Events.load_event_from_template(template="fixtures/events/tag-account-template.json",
                                            context=dict(account="123456789012",
                                                         new_state=State.RELEASED.value))
    result = handle_tag_event(event=event, context=None, session=session)
    assert result['Source'] == 'SustainablePersonalAccounts'
    assert result['DetailType'] == 'ReleasedAccount'
    details = json.loads(result['Detail'])
    assert details['Environment'] == 'envt1'
    assert details['Account'] == '123456789012'
    assert details.get('Message') is None


@pytest.mark.integration_tests
@patch.dict(os.environ, dict(ACCOUNTS_PARAMETER="Accounts",
                             EVENT_BUS_ARN='arn:aws',
                             ORGANIZATIONAL_UNITS_PARAMETER="OrganizationalUnits",
                             VERBOSITY='INFO'))
def test_handle_tag_event_on_unexpected_state(session):
    event = Events.load_event_from_template(template="fixtures/events/tag-account-template.json",
                                            context=dict(account="123456789012",
                                                         new_state=State.VANILLA.value))
    result = handle_tag_event(event=event, context=None, session=session)
    assert result == "[DEBUG] Unexpected state 'vanilla' for this function"
