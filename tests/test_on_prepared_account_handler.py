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

from unittest.mock import patch
import os
import pytest

from code import Events
from code.on_prepared_account_handler import handle_codebuild_event, handle_local_event
from code.worker import Worker


# pytestmark = pytest.mark.wip


@patch.dict(os.environ, dict(DRY_RUN="TRUE",
                             VERBOSITY='DEBUG'))
def test_handle_codebuild_event():
    event = Events.make_event(template="tests/events/codebuild-template.json",
                              context=dict(account="123456789012",
                                           project=Worker.PROJECT_NAME_FOR_ACCOUNT_PREPARATION,
                                           status="SUCCEEDED"))
    result = handle_codebuild_event(event=event, context=None)
    assert result == {'Detail': '{"Account": "123456789012", "Environment": "Spa"}', 'DetailType': 'PreparedAccount', 'Source': 'SustainablePersonalAccounts'}


@patch.dict(os.environ, dict(DRY_RUN="TRUE",
                             VERBOSITY='INFO'))
def test_handle_codebuild_event_on_unexpected_project():
    event = Events.make_event(template="tests/events/codebuild-template.json",
                              context=dict(account="123456789012",
                                           project="SampleProject",
                                           status="SUCCEEDED"))
    result = handle_codebuild_event(event=event, context=None)
    assert result == "[DEBUG] Ignored project 'SampleProject'"


@patch.dict(os.environ, dict(DRY_RUN="TRUE",
                             VERBOSITY='INFO'))
def test_handle_codebuild_event_on_unexpected_status():
    event = Events.make_event(template="tests/events/codebuild-template.json",
                              context=dict(account="123456789012",
                                           project=Worker.PROJECT_NAME_FOR_ACCOUNT_PREPARATION,
                                           status="FAILED"))
    result = handle_codebuild_event(event=event, context=None)
    assert result == "[DEBUG] Ignored status 'FAILED'"


@patch.dict(os.environ, dict(DRY_RUN="TRUE",
                             ENVIRONMENT_IDENTIFIER="envt1",
                             VERBOSITY='DEBUG'))
def test_handle_local_event():
    event = Events.make_event(template="tests/events/local-event-template.json",
                              context=dict(account="123456789012",
                                           label="PreparedAccount",
                                           environment="envt1"))
    result = handle_local_event(event=event, context=None)
    assert result == {'Detail': '{"Account": "123456789012", "Environment": "envt1"}', 'DetailType': 'ReleasedAccount', 'Source': 'SustainablePersonalAccounts'}


@patch.dict(os.environ, dict(DRY_RUN="TRUE",
                             ENVIRONMENT_IDENTIFIER="envt1",
                             VERBOSITY='INFO'))
def test_handle_local_event_on_unexpected_environment():
    event = Events.make_event(template="tests/events/local-event-template.json",
                              context=dict(account="123456789012",
                                           label="PreparedAccount",
                                           environment="alien*environment"))

    result = handle_local_event(event=event, context=None)
    assert result == "[DEBUG] Unexpected environment 'alien*environment'"


@patch.dict(os.environ, dict(DRY_RUN="TRUE",
                             ENVIRONMENT_IDENTIFIER="envt1",
                             VERBOSITY='INFO'))
def test_handle_local_event_on_unexpected_label():
    event = Events.make_event(template="tests/events/local-event-template.json",
                              context=dict(account="123456789012",
                                           label="CreatedAccount",
                                           environment="envt1"))

    result = handle_local_event(event=event, context=None)
    assert result == "[DEBUG] Unexpected event label 'CreatedAccount'"
