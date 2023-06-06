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

import io
from unittest.mock import patch
from moto import mock_cloudwatch, mock_dynamodb, mock_events, mock_organizations
import os
from cProfile import Profile
from pstats import Stats
import pytest

from lambdas import Events
from lambdas.on_transaction_metering_handler import handle_account_event, handle_stream_event

# pytestmark = pytest.mark.wip
from tests.fixture_key_value_store import create_my_table


@pytest.mark.integration_tests
@patch.dict(os.environ, dict(ENVIRONMENT_IDENTIFIER="envt1",
                             METERING_TRANSACTIONS_DATASTORE="my_table",
                             VERBOSITY='DEBUG'))
@mock_cloudwatch
@mock_dynamodb
@mock_organizations
def test_handle_account_event_for_maintenance_transaction():
    create_my_table()

    def my_emit_spa_event(label, payload):
        assert label == 'SuccessfulMaintenanceEvent'
        assert set(payload.keys()) == {'transaction', 'account', 'cost-center', 'begin', 'end'}
        assert payload['account'] == "123456789012"
        assert payload['transaction'] == 'maintenance'

    expired = Events.load_event_from_template(template="fixtures/events/account-event-template.json",
                                              context=dict(account="123456789012",
                                                           label="ExpiredAccount",
                                                           environment="envt1"))
    released = Events.load_event_from_template(template="fixtures/events/account-event-template.json",
                                               context=dict(account="123456789012",
                                                            label="ReleasedAccount",
                                                            environment="envt1"))

    with Profile() as profiler:
        assert handle_account_event(event=expired, emit=my_emit_spa_event) == '[OK] ExpiredAccount 123456789012'
        assert handle_account_event(event=released, emit=my_emit_spa_event) == '[OK] ReleasedAccount 123456789012'
    stream = io.StringIO()
    stats = Stats(profiler, stream=stream).sort_stats('cumulative')
    stats.print_stats('[^w/]+/lambdas/', 10)
    print(stream.getvalue())


@pytest.mark.integration_tests
@patch.dict(os.environ, dict(ENVIRONMENT_IDENTIFIER="envt1",
                             METERING_TRANSACTIONS_DATASTORE="my_table",
                             VERBOSITY='DEBUG'))
@mock_cloudwatch
@mock_dynamodb
@mock_organizations
def test_handle_account_event_for_on_boarding_transaction():
    create_my_table()

    def my_emit_spa_event(label, payload):
        assert label == 'SuccessfulOnBoardingEvent'
        assert set(payload.keys()) == {'transaction', 'account', 'cost-center', 'begin', 'end'}
        assert payload['account'] == "123456789012"
        assert payload['transaction'] == 'on-boarding'

    created = Events.load_event_from_template(template="fixtures/events/account-event-template.json",
                                              context=dict(account="123456789012",
                                                           label="CreatedAccount",
                                                           environment="envt1"))
    released = Events.load_event_from_template(template="fixtures/events/account-event-template.json",
                                               context=dict(account="123456789012",
                                                            label="ReleasedAccount",
                                                            environment="envt1"))
    with Profile() as profiler:
        assert handle_account_event(event=created, emit=my_emit_spa_event) == '[OK] CreatedAccount 123456789012'
        assert handle_account_event(event=released, emit=my_emit_spa_event) == '[OK] ReleasedAccount 123456789012'
    stream = io.StringIO()
    stats = Stats(profiler, stream=stream).sort_stats('cumulative')
    stats.print_stats('[^w/]+/lambdas/', 10)
    print(stream.getvalue())


@pytest.mark.integration_tests
@patch.dict(os.environ, dict(ENVIRONMENT_IDENTIFIER="envt1",
                             METERING_TRANSACTIONS_DATASTORE="my_table",
                             VERBOSITY='INFO'))
@mock_cloudwatch
@mock_dynamodb
@mock_events
@mock_organizations
def test_handle_account_event():
    create_my_table()

    for label in Events.ACCOUNT_EVENT_LABELS:
        event = Events.load_event_from_template(template="fixtures/events/account-event-template.json",
                                                context=dict(account="123456789012",
                                                             label=label,
                                                             environment="envt1"))
        assert handle_account_event(event=event) == f"[OK] {label} 123456789012"


@pytest.mark.unit_tests
@patch.dict(os.environ, dict(ENVIRONMENT_IDENTIFIER="envt1",
                             VERBOSITY='INFO'))
def test_handle_account_event_on_unexpected_environment():
    event = Events.load_event_from_template(template="fixtures/events/account-event-template.json",
                                            context=dict(account="123456789012",
                                                         label="CreatedAccount",
                                                         environment="alien*environment"))
    assert handle_account_event(event=event) == "[DEBUG] Unexpected environment 'alien*environment'"


@pytest.mark.unit_tests
@patch.dict(os.environ, dict(ENVIRONMENT_IDENTIFIER="envt1",
                             VERBOSITY='INFO'))
@mock_events
def test_handle_stream_event_on_expired_transaction():
    event = Events.load_event_from_template(template="fixtures/events/dynamodb-expiration-event-template.json",
                                            context={})
    assert handle_stream_event(event=event) == "[OK]"