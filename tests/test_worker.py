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

import os
from unittest.mock import Mock, patch
import pytest
from types import SimpleNamespace

from code import Worker


pytestmark = pytest.mark.wip


@pytest.fixture
def session():
    mock = Mock()
    mock.client.return_value.create_policy.return_value = dict(Policy=dict(Arn='arn:aws'))
    mock.client.return_value.create_project.return_value = dict(project=dict(arn='arn:aws'))
    mock.client.return_value.get_role.return_value = dict(Role=dict(Arn='arn:aws'))
    return mock


@patch.dict(os.environ, dict(DRY_RUN="true", ROLE_ARN_TO_MANAGE_ACCOUNTS='some_role'))
def test_get_session():
    pass

    # handle = Mock()
    # handle.client.return_value.assume_role.return_value = dict(Credentials=dict(AccessKeyId='ak',
    #                                                                             SecretAccessKey='sk',
    #                                                                             SessionToken='token'))
    # Worker.get_session(account='123456789012', session=handle)


@patch.dict(os.environ, dict(DRY_RUN="true"))
def test_deploy_project(session):
    Worker.deploy_project(name='name', description='description', buildspec='buildspec', role='role', session=session)
    session.client.assert_called_with('codebuild')
    session.client.return_value.create_project.assert_called()


# def test_deploy_role_for_events():
#     Worker.deploy_role_for_events(event_bus_arn='arn:aws')
#     assert False
#

@patch.dict(os.environ, dict(DRY_RUN="true"))
def test_prepare(session):
    account = SimpleNamespace(id='123456789012', email='a@b.com', unit='ou-1234')
    Worker.prepare(account=account, organizational_units={}, buildspec='hello_world', event_bus_arn='arn:aws', session=session)


@patch.dict(os.environ, dict(DRY_RUN="true"))
def test_purge(session):
    account = SimpleNamespace(id='123456789012', email='a@b.com', unit='ou-1234')
    Worker.purge(account=account, organizational_units={}, buildspec='hello_again', event_bus_arn='arn:aws', session=session)


def test_make_prepare_variables():
    account = SimpleNamespace(id='123456789012', email='a@b.com', unit='ou-1234')
    organizational_units = {'ou-1234': {'cost_budget': '500.0'}, 'ou-5678': {'cost_budget': '300'}}
    variables = Worker.make_prepare_variables(account=account, organizational_units=organizational_units)
    assert variables == {'BUDGET_AMOUNT': '500.0', 'BUDGET_EMAIL': 'a@b.com'}


def test_make_purge_variables():
    account = SimpleNamespace(id='123456789012', email='a@b.com', unit='ou-1234')
    organizational_units = {'ou-1234': {'cost_budget': '500.0'}, 'ou-5678': {'cost_budget': '300'}}
    variables = Worker.make_purge_variables(account=account, organizational_units=organizational_units)
    assert variables == {'PURGE_EMAIL': 'a@b.com'}
