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

import json
from unittest.mock import Mock
import pytest

from code import EventFactory

# pytestmark = pytest.mark.wip


def test_emit():
    mock = Mock()
    EventFactory.emit(label='CreatedAccount', account='123456789012', session=mock)
    mock.client.assert_called_with('events')
    mock.client.return_value.put_events.assert_called_with(Entries=[
        {'Detail': '{"Account": "123456789012"}',
         'DetailType': 'CreatedAccount',
         'Source': 'SustainablePersonalAccounts'}])


def test_build_event():
    event = EventFactory.build_event(label='CreatedAccount', account='123456789012')
    assert json.loads(event['Detail'])['Account'] == '123456789012'
    assert event['DetailType'] == 'CreatedAccount'
    assert event['Source'] == 'SustainablePersonalAccounts'


def test_state_labels():
    for label in EventFactory.STATE_LABELS:
        event = EventFactory.build_event(label=label, account='123456789012')
        assert event['DetailType'] == label

    with pytest.raises(AttributeError):
        EventFactory.build_event(label='*perfectly*unknown*', account='123456789012')


def test_put_event():
    mock = Mock()
    EventFactory.put_event(event='hello', session=mock)
    mock.client.assert_called_with('events')
    mock.client.return_value.put_events.assert_called_with(Entries=['hello'])


def test_decode_local_event():

    # where we accept any event with valid account identifier
    event = EventFactory.make_event(template="tests/events/local-event-template.json",
                                    context=dict(account="123456789012",
                                                 state="CreatedAccount"))
    decoded = EventFactory.decode_local_event(event)
    assert decoded.account == "123456789012"
    assert decoded.state == "CreatedAccount"

    # where we reject events with malformed account identifier
    event = EventFactory.make_event(template="tests/events/local-event-template.json",
                                    context=dict(account="short",
                                                 state="CreatedAccount"))
    with pytest.raises(ValueError):
        EventFactory.decode_local_event(event)

    # where we reject events with unexpected state
    event = EventFactory.make_event(template="tests/events/local-event-template.json",
                                    context=dict(account="123456789012",
                                                 state="CreatedAccount"))
    with pytest.raises(ValueError):
        EventFactory.decode_local_event(event, match='PurgedAccount')


def test_decode_move_account_event():

    # where we accept any event with valid account identifier
    event = EventFactory.make_event(template="tests/events/move-account-template.json",
                                    context=dict(account="123456789012",
                                                 destination_organizational_unit="ou-destination",
                                                 source_organizational_unit="ou-source"))
    decoded = EventFactory.decode_move_account_event(event)
    assert decoded.account == "123456789012"
    assert decoded.organizational_unit == "ou-destination"

    # where we reject events with malformed account identifier
    event = EventFactory.make_event(template="tests/events/move-account-template.json",
                                    context=dict(account="short",
                                                 destination_organizational_unit="ou-destination",
                                                 source_organizational_unit="ou-source"))
    with pytest.raises(ValueError):
        EventFactory.decode_move_account_event(event)

    # where we reject events with unexpected destination
    event = EventFactory.make_event(template="tests/events/move-account-template.json",
                                    context=dict(account="123456789012",
                                                 destination_organizational_unit="ou-expected",
                                                 source_organizational_unit="ou-source"))
    with pytest.raises(ValueError):
        EventFactory.decode_move_account_event(event, match="ou-destination")
