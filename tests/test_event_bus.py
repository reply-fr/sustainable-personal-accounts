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

from code.event_bus import EventFactory


# pytestmark = pytest.mark.wip


def test_emit():
    client = Mock()
    EventFactory.emit(label='CreatedAccount', account='1234567890', client=client)
    client.put_events.assert_called_with(Entries=[
        {'Detail': '{"Account": "1234567890"}',
         'DetailType': 'CreatedAccount',
         'Source': 'SustainablePersonalAccounts'}])


def test_build_event():
    event = EventFactory.build_event(label='CreatedAccount', account='1234567890')
    assert json.loads(event['Detail'])['Account'] == '1234567890'
    assert event['DetailType'] == 'CreatedAccount'
    assert event['Source'] == 'SustainablePersonalAccounts'


def test_accepted_labels():
    for label in EventFactory.ACCEPTED_LABELS:
        event = EventFactory.build_event(label=label, account='1234567890')
        assert event['DetailType'] == label

    with pytest.raises(AttributeError):
        EventFactory.build_event(label='*perfectly*unknown*', account='1234567890')


def test_put_event():
    client = Mock()
    EventFactory.put_event(event='hello', client=client)
    client.put_events.assert_called_with(Entries=['hello'])


def test_decode_aws_organizations_event():

    parameters = dict(account="1234567890",
                      destination_organizational_unit="ou-destination",
                      source_organizational_unit="ou-source")

    with open("tests/events/move-account-template.json") as stream:
        text = stream.read()
        for key, value in parameters.items():
            text = text.replace('{' + key + '}', value)
        event = json.loads(text)

    decoded = EventFactory.decode_aws_organizations_event(event)
    assert decoded.account == "1234567890"
    assert decoded.organizational_unit == "ou-destination"
