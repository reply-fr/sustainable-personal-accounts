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
from moto import mock_dynamodb, mock_organizations
import os
import pytest

from code import Events
from code.on_account_event_then_shadow_handler import handle_account_event
from code.key_value_store import KeyValueStore

from tests.fixture_key_value_store import create_my_table
pytestmark = pytest.mark.wip


@pytest.mark.unit_tests
@patch.dict(os.environ, dict(ENVIRONMENT_IDENTIFIER="envt1",
                             METERING_SHADOWS_DATASTORE="my_table",
                             VERBOSITY='DEBUG'))
@mock_dynamodb
@mock_organizations
def test_handle_account_event():
    create_my_table()

    for label in Events.ACCOUNT_EVENT_LABELS:
        event = Events.load_event_from_template(template="fixtures/events/account-event-template.json",
                                                context=dict(account="123456789012",
                                                             label=label,
                                                             environment="envt1"))
        assert handle_account_event(event=event) == f"[OK] {label} 123456789012"

    instance = KeyValueStore(table_name="my_table")
    record = instance.retrieve(key="123456789012")
    print(record)
    print(record.keys())
    assert record['last_state'] == 'ReleasedAccount'
    assert set(record['stamps'].keys()) == set(Events.ACCOUNT_EVENT_LABELS)
    assert 'last_preparation_log' in record.keys()
    assert 'last_purge_log' in record.keys()


@pytest.mark.unit_tests
@patch.dict(os.environ, dict(ENVIRONMENT_IDENTIFIER="envt1",
                             VERBOSITY='INFO'))
def test_handle_account_event_on_unexpected_environment():
    event = Events.load_event_from_template(template="fixtures/events/account-event-template.json",
                                            context=dict(account="123456789012",
                                                         label="CreatedAccount",
                                                         environment="alien*environment"))
    assert handle_account_event(event=event) == "[DEBUG] Unexpected environment 'alien*environment'"
