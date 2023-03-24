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

from lambdas import Events
from lambdas.on_account_event_handler import handle_account_event

# pytestmark = pytest.mark.wip


@pytest.mark.unit_tests
@patch.dict(os.environ, dict(ENVIRONMENT_IDENTIFIER="envt1",
                             VERBOSITY='DEBUG'))
def test_handle_account_event():
    event = Events.load_event_from_template(template="fixtures/events/account-event-template.json",
                                            context=dict(account="123456789012",
                                                         label="CreatedAccount",
                                                         environment="envt1"))
    mock = Mock()
    assert handle_account_event(event=event, context=None, session=mock) == '[OK] CreatedAccount 123456789012'


@pytest.mark.unit_tests
@patch.dict(os.environ, dict(ENVIRONMENT_IDENTIFIER="envt1",
                             VERBOSITY='DEBUG'))
def test_handle_preparation_report_event():
    event = Events.load_event_from_template(template="fixtures/events/report-event-template.json",
                                            context=dict(account="123456789012",
                                                         label="PreparationReport",
                                                         message="some log",
                                                         environment="envt1"))
    mock = Mock()
    assert handle_account_event(event=event, context=None, session=mock) == '[OK] PreparationReport 123456789012'


@pytest.mark.unit_tests
@patch.dict(os.environ, dict(ENVIRONMENT_IDENTIFIER="envt1",
                             VERBOSITY='DEBUG'))
def test_handle_purge_report_event():
    event = Events.load_event_from_template(template="fixtures/events/report-event-template.json",
                                            context=dict(account="123456789012",
                                                         label="PurgeReport",
                                                         message="some log",
                                                         environment="envt1"))
    mock = Mock()
    assert handle_account_event(event=event, context=None, session=mock) == '[OK] PurgeReport 123456789012'


@pytest.mark.unit_tests
@patch.dict(os.environ, dict(ENVIRONMENT_IDENTIFIER="envt1",
                             VERBOSITY='INFO'))
def test_handle_account_event_on_unexpected_environment():
    event = Events.load_event_from_template(template="fixtures/events/account-event-template.json",
                                            context=dict(account="123456789012",
                                                         label="CreatedAccount",
                                                         environment="alien*environment"))
    mock = Mock()
    assert handle_account_event(event=event, context=None, session=mock) == "[DEBUG] Unexpected environment 'alien*environment'"