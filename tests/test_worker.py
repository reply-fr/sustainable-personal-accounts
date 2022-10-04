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

from boto3 import Session
import json
from unittest.mock import Mock, patch
from moto import mock_sns
import os
import pytest
from types import SimpleNamespace

from code import Worker

# pytestmark = pytest.mark.wip


@pytest.fixture
def session():
    mock = Mock()
    mock.client.return_value.create_policy.return_value = dict(Policy=dict(Arn='arn:aws'))
    mock.client.return_value.create_project.return_value = dict(project=dict(arn='arn:aws'))
    mock.client.return_value.create_topic.return_value = dict(TopicArn='arn:aws')
    mock.client.return_value.get_role.return_value = dict(Role=dict(Arn='arn:aws'))
    return mock


def test_deploy_project(session):
    Worker.deploy_project(name='name', description='description', buildspec='buildspec', role='role', session=session)
    session.client.assert_called_with('codebuild')
    session.client.return_value.create_project.assert_called()


@patch.dict(os.environ, dict(ENVIRONMENT_IDENTIFIER="JustForTest",
                             TOPIC_ARN='arn:aws:test'))
def test_get_preparation_variables():
    account = SimpleNamespace(id='123456789012', email='a@b.com', unit='ou-1234')
    settings = dict(preparation=dict(variables=dict(BUDGET_AMOUNT='500.0')))
    event_bus_arn = 'arn:aws:bus'
    topic_arn = 'arn:aws:topic'
    variables = Worker.get_preparation_variables(account=account, settings=settings, event_bus_arn=event_bus_arn, topic_arn=topic_arn)
    assert variables == {'BUDGET_AMOUNT': '500.0',
                         'BUDGET_EMAIL': 'a@b.com',
                         'ENVIRONMENT_IDENTIFIER': 'JustForTest',
                         'EVENT_BUS_ARN': 'arn:aws:bus',
                         'TOPIC_ARN': 'arn:aws:topic'}


@patch.dict(os.environ, dict(ENVIRONMENT_IDENTIFIER="JustForTest",
                             TOPIC_ARN='arn:aws:test'))
def test_get_purge_variables():
    account = SimpleNamespace(id='123456789012', email='a@b.com', unit='ou-1234')
    settings = dict(purge=dict(variables=dict(MAXIMUM_AGE='1M')))
    event_bus_arn = 'arn:aws:bus'
    variables = Worker.get_purge_variables(account=account, settings=settings, event_bus_arn=event_bus_arn)
    assert variables == {'EVENT_BUS_ARN': 'arn:aws:bus',
                         'ENVIRONMENT_IDENTIFIER': 'JustForTest',
                         'MAXIMUM_AGE': '1M',
                         'PURGE_EMAIL': 'a@b.com',
                         'TOPIC_ARN': 'arn:aws:test'}


@mock_sns
def test_grant_publishing_from_budgets():
    session = Session()
    topic_arn = session.client('sns').create_topic(Name='test')['TopicArn']

    Worker.grant_publishing_from_budgets(topic_arn=topic_arn)

    attributes = session.client('sns').get_topic_attributes(TopicArn=topic_arn)
    policy = json.loads(attributes['Attributes']['Policy'])
    found = False
    for statement in policy['Statement']:
        if statement['Sid'] == "GrantPublishingFromBudgets":
            found = True
    assert found


@patch.dict(os.environ, dict(AUTOMATION_ACCOUNT="123456789012"))
def test_prepare(session):
    account = SimpleNamespace(id='123456789012', email='a@b.com', unit='ou-1234')
    Worker.prepare(account=account, settings={}, buildspec='hello_world', event_bus_arn='arn:aws', topic_arn='arn:aws', session=session)


def test_purge(session):
    account = SimpleNamespace(id='123456789012', email='a@b.com', unit='ou-1234')
    Worker.purge(account=account, settings={}, buildspec='hello_again', event_bus_arn='arn:aws', session=session)
