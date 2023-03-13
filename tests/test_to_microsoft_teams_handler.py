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

from boto3.session import Session
from unittest.mock import patch
import os
import pytest
from types import SimpleNamespace

from account import Account
from code.to_microsoft_teams_handler import handle_spa_event, post_message
from events import Events

# pytestmark = pytest.mark.wip


@pytest.mark.integration_tests
@patch.dict(os.environ, dict(ENVIRONMENT_IDENTIFIER="envt1"))
def test_handle_spa_event(monkeypatch):

    def mock_account_describe(id, *args, **kwargs):
        return SimpleNamespace(id=id, email='a@b.com')

    monkeypatch.setattr(Account, 'describe', mock_account_describe)

    session = Session(aws_access_key_id='testing',
                      aws_secret_access_key='testing',
                      aws_session_token='testing',
                      region_name='eu-west-1')

    event = Events.load_event_from_template(template="fixtures/events/spa-event-template.json",
                                            context=dict(label="MessageToMicrosoftTeams",
                                                         payload='{"hello": "world"}',
                                                         environment="envt1"))

    result = handle_spa_event(event=event, context=None, session=session)
    assert result == '[OK]'


@pytest.mark.unit_tests
@patch.dict(os.environ, dict(MICROSOFT_WEBHOOK_ON_ALERTS='https://webhook/'))
@patch('pymsteams.connectorcard')
def test_post_message(patched):
    message = dict(Message='hello world',
                   Subject='some subject')
    post_message(message=message)
    patched.assert_called_once_with('https://webhook/')
    message = patched('https://webhook/')
    message.title.assert_called_once_with('some subject')
    message.text.assert_called_once_with('hello world')
    message.send.assert_called_once()
