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
from unittest.mock import Mock, patch
import os
import pytest

from code import Events, State

# pytestmark = pytest.mark.wip


@patch.dict(os.environ, dict(DRY_RUN="FALSE"))
def test_emit():
    mock = Mock()
    Events.emit(label='CreatedAccount', account='123456789012', session=mock)
    mock.client.assert_called_with('events')
    mock.client.return_value.put_events.assert_called_with(Entries=[
        {'Detail': '{"Account": "123456789012"}',
         'DetailType': 'CreatedAccount',
         'Source': 'SustainablePersonalAccounts'}])


def test_build_event():
    event = Events.build_event(label='CreatedAccount', account='123456789012')
    assert json.loads(event['Detail'])['Account'] == '123456789012'
    assert event['DetailType'] == 'CreatedAccount'
    assert event['Source'] == 'SustainablePersonalAccounts'


def test_build_event_on_invalid_account():
    with pytest.raises(ValueError):
        Events.build_event(label='CreatedAccount', account='short')


def test_build_event_with_labels():
    for label in Events.EVENT_LABELS:
        event = Events.build_event(label=label, account='123456789012')
        assert event['DetailType'] == label

    with pytest.raises(ValueError):
        Events.build_event(label='*perfectly*unknown*', account='123456789012')


def test_decode_codebuild_event():
    event = Events.make_event(template="tests/events/codebuild-template.json",
                              context=dict(account="123456789012",
                                           project="SampleProject",
                                           status="SUCCEEDED"))
    decoded = Events.decode_codebuild_event(event)
    assert decoded.account == "123456789012"
    assert decoded.project == "SampleProject"
    assert decoded.status == "SUCCEEDED"


def test_decode_codebuild_event_on_malformed_account():
    event = Events.make_event(template="tests/events/codebuild-template.json",
                              context=dict(account="short",
                                           project="SampleProject",
                                           status="SUCCEEDED"))
    with pytest.raises(ValueError):
        Events.decode_codebuild_event(event)


def test_decode_codebuild_event_on_unexpected_project():
    event = Events.make_event(template="tests/events/codebuild-template.json",
                              context=dict(account="123456789012",
                                           project="NotMyProjectProject",
                                           status="SUCCEEDED"))
    with pytest.raises(ValueError):
        Events.decode_codebuild_event(event, match="ExpectedProject")


def test_decode_codebuild_event_on_unexpected_status():
    event = Events.make_event(template="tests/events/codebuild-template.json",
                              context=dict(account="123456789012",
                                           project="SampleProject",
                                           status="FAILED"))
    with pytest.raises(ValueError):
        Events.decode_codebuild_event(event)


def test_decode_local_event():
    event = Events.make_event(template="tests/events/local-event-template.json",
                              context=dict(account="123456789012",
                                           label="CreatedAccount"))
    decoded = Events.decode_local_event(event)
    assert decoded.account == "123456789012"
    assert decoded.label == "CreatedAccount"


def test_decode_local_event_on_malformed_account():
    event = Events.make_event(template="tests/events/local-event-template.json",
                              context=dict(account="short",
                                           label="CreatedAccount"))
    with pytest.raises(ValueError):
        Events.decode_local_event(event)


def test_decode_local_event_on_unexpected_label():
    event = Events.make_event(template="tests/events/local-event-template.json",
                              context=dict(account="123456789012",
                                           label="CreatedAccount"))
    with pytest.raises(ValueError):
        Events.decode_local_event(event, match='PurgedAccount')


def test_decode_move_account_event():
    event = Events.make_event(template="tests/events/move-account-template.json",
                              context=dict(account="123456789012",
                                           destination_organizational_unit="ou-destination",
                                           source_organizational_unit="ou-source"))
    decoded = Events.decode_move_account_event(event)
    assert decoded.account == "123456789012"
    assert decoded.organizational_unit == "ou-destination"


def test_decode_move_account_event_on_malformed_account():
    event = Events.make_event(template="tests/events/move-account-template.json",
                              context=dict(account="short",
                                           destination_organizational_unit="ou-destination",
                                           source_organizational_unit="ou-source"))
    with pytest.raises(ValueError):
        Events.decode_move_account_event(event)


def test_decode_move_account_event_on_unexpected_organizational_unit():
    event = Events.make_event(template="tests/events/move-account-template.json",
                              context=dict(account="123456789012",
                                           destination_organizational_unit="ou-expected",
                                           source_organizational_unit="ou-source"))
    with pytest.raises(ValueError):
        Events.decode_move_account_event(event, matches=["ou-destination"])


def test_decode_tag_account_event():
    event = Events.make_event(template="tests/events/tag-account-template.json",
                              context=dict(account="123456789012",
                                           new_state="assigned"))
    decoded = Events.decode_tag_account_event(event)
    assert decoded.account == "123456789012"
    assert decoded.state == "assigned"


def test_decode_tag_account_event_on_malformed_account():
    event = Events.make_event(template="tests/events/tag-account-template.json",
                              context=dict(account="short",
                                           new_state="assigned"))
    with pytest.raises(ValueError):
        Events.decode_tag_account_event(event)


def test_decode_tag_account_event_on_unexpected_state():
    event = Events.make_event(template="tests/events/tag-account-template.json",
                              context=dict(account="123456789012",
                                           new_state="assigned"))
    with pytest.raises(ValueError):
        Events.decode_tag_account_event(event, match=State.EXPIRED)


def test_decode_tag_account_event_on_missing_state():
    event = Events.make_event(template="tests/events/tag-account-template.json",
                              context=dict(account="123456789012"))

    # remove tag 'account:state' from regular fixture
    tags = event["detail"]["requestParameters"]["tags"]
    tags = [item for item in tags if item['key'] != 'account:state']
    event["detail"]["requestParameters"]["tags"] = tags

    with pytest.raises(ValueError):
        Events.decode_tag_account_event(event)


@patch.dict(os.environ, dict(DRY_RUN="FALSE"))
def test_put_event():
    mock = Mock()
    Events.put_event(event='hello', session=mock)
    mock.client.assert_called_with('events')
    mock.client.return_value.put_events.assert_called_with(Entries=['hello'])
