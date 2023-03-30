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

from lambdas import Events, State

# pytestmark = pytest.mark.wip


@pytest.mark.unit_tests
def test_build_account_event():
    event = Events.build_account_event(label='PurgeReport', account='123456789012', message='some log')
    assert event['Source'] == 'SustainablePersonalAccounts'
    assert event['DetailType'] == 'PurgeReport'
    details = json.loads(event['Detail'])
    assert details['Account'] == '123456789012'
    assert details['Message'] == 'some log'


@pytest.mark.unit_tests
def test_build_account_event_on_invalid_account():
    with pytest.raises(ValueError):
        Events.build_account_event(label='CreatedAccount', account='short')


@pytest.mark.unit_tests
def test_build_account_event_with_labels():
    for label in Events.ACCOUNT_EVENT_LABELS:
        event = Events.build_account_event(label=label, account='123456789012')
        assert event['DetailType'] == label

    with pytest.raises(ValueError):
        Events.build_account_event(label='*perfectly*unknown*', account='123456789012')


@pytest.mark.unit_tests
def test_build_spa_event():
    event = Events.build_spa_event(label='MessageToMicrosoftTeams', payload='hello world')
    assert event['Source'] == 'SustainablePersonalAccounts'
    assert event['DetailType'] == 'MessageToMicrosoftTeams'
    details = json.loads(event['Detail'])
    assert details['Payload'] == 'hello world'
    assert details['ContentType'] == 'application/json'


@pytest.mark.unit_tests
def test_build_spa_event_with_labels():
    for label in Events.SPA_EVENT_LABELS:
        event = Events.build_spa_event(label=label)
        assert event['DetailType'] == label

    with pytest.raises(ValueError):
        Events.build_spa_event(label='*perfectly*unknown*')


@pytest.mark.unit_tests
@patch.dict(os.environ, dict(ENVIRONMENT_IDENTIFIER="envt1"))
def test_decode_account_event():
    event = Events.load_event_from_template(template="fixtures/events/account-event-template.json",
                                            context=dict(account="123456789012",
                                                         label="CreatedAccount",
                                                         environment="envt1"))
    decoded = Events.decode_account_event(event)
    assert decoded.account == "123456789012"
    assert decoded.label == "CreatedAccount"


@pytest.mark.unit_tests
@patch.dict(os.environ, dict(ENVIRONMENT_IDENTIFIER="envt1"))
def test_decode_account_event_on_unexpected_environment():
    event = Events.load_event_from_template(template="fixtures/events/account-event-template.json",
                                            context=dict(account="short",
                                                         label="CreatedAccount",
                                                         environment="alien*environment"))
    with pytest.raises(ValueError):
        Events.decode_account_event(event)


@pytest.mark.unit_tests
@patch.dict(os.environ, dict(ENVIRONMENT_IDENTIFIER="envt1"))
def test_decode_account_event_on_malformed_account():
    event = Events.load_event_from_template(template="fixtures/events/account-event-template.json",
                                            context=dict(account="short",
                                                         label="CreatedAccount",
                                                         environment="envt1"))
    with pytest.raises(ValueError):
        Events.decode_account_event(event)


@pytest.mark.unit_tests
@patch.dict(os.environ, dict(ENVIRONMENT_IDENTIFIER="envt1"))
def test_decode_account_event_on_unexpected_label():
    event = Events.load_event_from_template(template="fixtures/events/account-event-template.json",
                                            context=dict(account="123456789012",
                                                         label="CreatedAccount",
                                                         environment="envt1"))
    with pytest.raises(ValueError):
        Events.decode_account_event(event, match='PurgedAccount')


@pytest.mark.unit_tests
def test_decode_codebuild_event():
    event = Events.load_event_from_template(template="fixtures/events/codebuild-template.json",
                                            context=dict(account="123456789012",
                                                         project="SampleProject",
                                                         status="SUCCEEDED"))
    decoded = Events.decode_codebuild_event(event)
    assert decoded.account == "123456789012"
    assert decoded.project == "SampleProject"
    assert decoded.status == "SUCCEEDED"


@pytest.mark.unit_tests
def test_decode_codebuild_event_on_malformed_account():
    event = Events.load_event_from_template(template="fixtures/events/codebuild-template.json",
                                            context=dict(account="short",
                                                         project="SampleProject",
                                                         status="SUCCEEDED"))
    with pytest.raises(ValueError):
        Events.decode_codebuild_event(event)


@pytest.mark.unit_tests
def test_decode_codebuild_event_on_unexpected_project():
    event = Events.load_event_from_template(template="fixtures/events/codebuild-template.json",
                                            context=dict(account="123456789012",
                                                         project="NotMyProjectProject",
                                                         status="SUCCEEDED"))
    with pytest.raises(ValueError):
        Events.decode_codebuild_event(event, match="ExpectedProject")


@pytest.mark.unit_tests
@patch.dict(os.environ, dict(ENVIRONMENT_IDENTIFIER="envt1"))
def test_decode_report_event():
    event = Events.load_event_from_template(template="fixtures/events/report-event-template.json",
                                            context=dict(account="123456789012",
                                                         label="PurgeReport",
                                                         message="some log",
                                                         environment="envt1"))
    decoded = Events.decode_account_event(event)
    assert decoded.account == "123456789012"
    assert decoded.label == "PurgeReport"
    assert decoded.message == "some log"


@pytest.mark.unit_tests
def test_decode_organization_event():
    event = Events.load_event_from_template(template="fixtures/events/move-account-template.json",
                                            context=dict(account="123456789012",
                                                         destination_organizational_unit="ou-destination",
                                                         source_organizational_unit="ou-source"))
    decoded = Events.decode_organization_event(event)
    assert decoded.account == "123456789012"
    assert decoded.organizational_unit == "ou-destination"


@pytest.mark.unit_tests
def test_decode_organization_event_on_malformed_account():
    event = Events.load_event_from_template(template="fixtures/events/move-account-template.json",
                                            context=dict(account="short",
                                                         destination_organizational_unit="ou-destination",
                                                         source_organizational_unit="ou-source"))
    with pytest.raises(ValueError):
        Events.decode_organization_event(event)


@pytest.mark.unit_tests
def test_decode_organization_event_on_unexpected_organizational_unit():
    event = Events.load_event_from_template(template="fixtures/events/move-account-template.json",
                                            context=dict(account="123456789012",
                                                         destination_organizational_unit="ou-expected",
                                                         source_organizational_unit="ou-source"))
    with pytest.raises(ValueError):
        Events.decode_organization_event(event, matches=["ou-destination"])


@pytest.mark.unit_tests
@patch.dict(os.environ, dict(ENVIRONMENT_IDENTIFIER="envt1"))
def test_decode_spa_event():
    event = Events.load_event_from_template(template="fixtures/events/spa-event-template.json",
                                            context=dict(label="MessageToMicrosoftTeams",
                                                         payload='{"hello": "world"}',
                                                         content_type='application/octet-stream',
                                                         environment="envt1"))
    decoded = Events.decode_spa_event(event)
    assert decoded.label == "MessageToMicrosoftTeams"
    assert decoded.payload == {"hello": "world"}
    assert decoded.content_type == 'application/octet-stream'


@pytest.mark.unit_tests
@patch.dict(os.environ, dict(ENVIRONMENT_IDENTIFIER="envt1"))
def test_decode_spa_event_on_unexpected_environment():
    event = Events.load_event_from_template(template="fixtures/events/spa-event-template.json",
                                            context=dict(label="MessageToMicrosoftTeams",
                                                         payload='{"hello": "world"}',
                                                         environment="alien*environment"))
    with pytest.raises(ValueError):
        Events.decode_spa_event(event)


@pytest.mark.unit_tests
@patch.dict(os.environ, dict(ENVIRONMENT_IDENTIFIER="envt1"))
def test_decode_spa_event_on_unexpected_label():
    event = Events.load_event_from_template(template="fixtures/events/spa-event-template.json",
                                            context=dict(label="CreatedAccount",
                                                         payload='{"hello": "world"}',
                                                         environment="envt1"))
    with pytest.raises(ValueError):
        Events.decode_spa_event(event, match='MessageToMicrosoftTeams')


@pytest.mark.unit_tests
def test_decode_tag_account_event():
    event = Events.load_event_from_template(template="fixtures/events/tag-account-template.json",
                                            context=dict(account="123456789012",
                                                         new_state="assigned"))
    decoded = Events.decode_tag_account_event(event)
    assert decoded.account == "123456789012"
    assert decoded.state == "assigned"


@pytest.mark.unit_tests
def test_decode_tag_account_event_on_malformed_account():
    event = Events.load_event_from_template(template="fixtures/events/tag-account-template.json",
                                            context=dict(account="short",
                                                         new_state="assigned"))
    with pytest.raises(ValueError):
        Events.decode_tag_account_event(event)


@pytest.mark.unit_tests
def test_decode_tag_account_event_on_unexpected_state():
    event = Events.load_event_from_template(template="fixtures/events/tag-account-template.json",
                                            context=dict(account="123456789012",
                                                         new_state="assigned"))
    with pytest.raises(ValueError):
        Events.decode_tag_account_event(event, match=State.EXPIRED)


@pytest.mark.unit_tests
def test_decode_tag_account_event_on_missing_state():
    event = Events.load_event_from_template(template="fixtures/events/tag-account-template.json",
                                            context=dict(account="123456789012"))

    # remove tag 'account-state' from regular fixture
    tags = event["detail"]["requestParameters"]["tags"]
    tags = [item for item in tags if item['key'] != 'account-state']
    event["detail"]["requestParameters"]["tags"] = tags

    with pytest.raises(ValueError):
        Events.decode_tag_account_event(event)


@pytest.mark.unit_tests
@patch.dict(os.environ, dict(ENVIRONMENT_IDENTIFIER='FromHere'))
def test_emit_account_event():
    mock = Mock()
    Events.emit_account_event(label='CreatedAccount', account='123456789012', message='message', session=mock)
    mock.client.assert_called_with('events')
    mock.client.return_value.put_events.assert_called_with(Entries=[
        {'Detail': '{"Account": "123456789012", "Environment": "FromHere", "Message": "message"}',
         'DetailType': 'CreatedAccount',
         'Source': 'SustainablePersonalAccounts'}])


@pytest.mark.unit_tests
@patch.dict(os.environ, dict(ENVIRONMENT_IDENTIFIER='FromHere'))
def test_emit_spa_event():
    mock = Mock()
    Events.emit_spa_event(label='MessageToMicrosoftTeams', payload='payload', session=mock)
    mock.client.assert_called_with('events')
    mock.client.return_value.put_events.assert_called_with(Entries=[
        {'Detail': '{"ContentType": "application/json", "Environment": "FromHere", "Payload": "payload"}',
         'DetailType': 'MessageToMicrosoftTeams',
         'Source': 'SustainablePersonalAccounts'}])


@pytest.mark.unit_tests
def test_put_event():
    mock = Mock()
    Events.put_event(event='hello', session=mock)
    mock.client.assert_called_with('events')
    mock.client.return_value.put_events.assert_called_with(Entries=['hello'])
