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

from base64 import b64encode
import boto3
import json
from unittest.mock import Mock, patch
from moto import mock_aws
import os
import pytest

from lambdas import Events
from lambdas.on_exception_handler import (handle_exception,
                                          handle_attachment_request,
                                          download_attachment,
                                          get_report_path,
                                          publish_notification_on_microsoft_teams,
                                          publish_notification_on_sns,
                                          store_report)

# pytestmark = pytest.mark.wip


sample_payload = json.dumps(
    {"message": "this is a message to describe the exception",
     "title": "exception has happened"})


@pytest.mark.integration_tests
@patch.dict(os.environ, dict(ENVIRONMENT_IDENTIFIER="envt1",
                             REPORTING_EXCEPTIONS_PREFIX="exceptions",
                             REPORTS_BUCKET_NAME="my_bucket",
                             RESPONSE_PLAN_ARN="arn:plan",
                             VERBOSITY='DEBUG',
                             WEB_ENDPOINTS_PARAMETER="my_endpoints"))
@mock_aws
def test_handle_exception():

    s3 = boto3.client("s3")
    s3.create_bucket(Bucket="my_bucket",
                     CreateBucketConfiguration=dict(LocationConstraint='eu-west-3'))

    ssm = boto3.client("ssm")
    ssm.put_parameter(Name='my_endpoints',
                      Value=json.dumps({"OnException.DownloadAttachment.WebEndpoint": "https://here"}),
                      Type='String')

    for label in Events.EXCEPTION_EVENT_LABELS:
        event = Events.load_event_from_template(template="fixtures/events/spa-event-template.json",
                                                context=dict(payload=sample_payload,
                                                             label=label,
                                                             environment="envt1"))
        mock = Mock()
        mock.client.return_value.start_incident.return_value = dict(incidentRecordArn="arn:incidents:123")
        mock.client.return_value.get_cost_and_usage.return_value = dict(ResultsByTime=[])
        assert handle_exception(event=event, context=None, session=mock) == f"[OK] {label}"

    event = {}
    mock = Mock()
    mock.client.return_value.start_incident.return_value = dict(incidentRecordArn="arn:incidents:123")
    mock.client.return_value.get_cost_and_usage.return_value = dict(ResultsByTime=[])
    assert handle_exception(event=event, context=None, session=mock) == "[OK] GenericException"


@pytest.mark.unit_tests
@patch.dict(os.environ, dict(ENVIRONMENT_IDENTIFIER="envt1",
                             VERBOSITY='INFO'))
def test_handle_exception_on_unexpected_environment():
    event = Events.load_event_from_template(template="fixtures/events/spa-event-template.json",
                                            context=dict(payload=sample_payload,
                                                         label="CreatedAccount",
                                                         environment="alien*environment"))
    mock = Mock()
    assert handle_exception(event=event, context=None, session=mock) == "[DEBUG] Unexpected environment 'alien*environment'"


@pytest.mark.unit_tests
@patch.dict(os.environ, dict(MICROSOFT_WEBHOOK_ON_ALERTS='https://webhook/'))
@mock_aws
def test_publish_notification_on_microsoft_teams():
    mock = Mock()
    notification = dict(Message='hello world',
                        Subject='some subject')
    publish_notification_on_microsoft_teams(notification=notification, session=mock)
    mock.client.assert_called_with('events')
    mock.client.return_value.put_events.assert_called_with(Entries=[{
        'Detail': '{"ContentType": "application/json", "Environment": "Spa", "Payload": {"Message": "hello world", "Subject": "some subject"}}',
        'DetailType': 'MessageToMicrosoftTeams',
        'Source': 'SustainablePersonalAccounts'}])


@pytest.mark.unit_tests
@patch.dict(os.environ, dict(TOPIC_ARN='aws:topic'))
@mock_aws
def test_publish_notification_on_sns():
    mock = Mock()
    notification = dict(Message='hello world',
                        Subject='some subject')
    publish_notification_on_sns(notification=notification, session=mock)
    mock.client.assert_called_with('sns')
    mock.client.return_value.publish.assert_called_with(TopicArn='aws:topic', Message='hello world', Subject='some subject')


@pytest.mark.unit_tests
@patch.dict(os.environ, dict(REPORTING_EXCEPTIONS_PREFIX='fake-prefix'))
def test_get_report_path():
    result = get_report_path(label='fake-label')
    assert 'fake-prefix' in result
    assert 'fake-label' in result


@pytest.mark.unit_tests
@patch.dict(os.environ, dict(REPORTS_BUCKET_NAME="my_bucket"))
@mock_aws
def test_store_report():
    s3 = boto3.client("s3")
    s3.create_bucket(Bucket="my_bucket",
                     CreateBucketConfiguration=dict(LocationConstraint='eu-west-3'))
    store_report(path="path/hello.txt", report="hello world") == '[OK]'


@pytest.mark.integration_tests
@patch.dict(os.environ, dict(ENVIRONMENT_IDENTIFIER="envt1",
                             REPORTING_EXCEPTIONS_PREFIX="exceptions",
                             REPORTS_BUCKET_NAME="my_bucket"))
@mock_aws
def test_handle_attachment_request():

    s3 = boto3.client("s3")
    s3.create_bucket(Bucket="my_bucket",
                     CreateBucketConfiguration=dict(LocationConstraint='eu-west-3'))
    s3.put_object(Bucket="my_bucket", Key="exceptions/my/test.csv", Body="hello,world\nhello,universe")

    with open('fixtures/events/sample_direct_download_request.json') as stream:
        assert handle_attachment_request(event=json.loads(stream.read())) == {
            'body': b64encode('hello,world\nhello,universe'.encode('utf-8')).decode(),
            'headers': {'Content-Disposition': 'attachment; filename="test.csv"',
                        'Content-Type': 'application/octet-stream'},
            'isBase64Encoded': True,
            'statusCode': 200}


@pytest.mark.integration_tests
@patch.dict(os.environ, dict(ENVIRONMENT_IDENTIFIER="envt1",
                             REPORTING_EXCEPTIONS_PREFIX="exceptions",
                             REPORTS_BUCKET_NAME="my_bucket"))
@mock_aws
def test_download_attachment():

    s3 = boto3.client("s3")
    s3.create_bucket(Bucket="my_bucket",
                     CreateBucketConfiguration=dict(LocationConstraint='eu-west-3'))
    s3.put_object(Bucket="my_bucket", Key="exceptions/my/test.csv", Body="hello,world\nhello,universe")

    sec_fetch_headers = {
        'sec-fetch-mode': 'navigate',
        'sec-fetch-dest': 'document',
        'sec-fetch-user': '?1',
        'sec-fetch-site': 'cross-site'
    }

    assert download_attachment(path="my/test.csv", headers=sec_fetch_headers) == {
        'body': b64encode('hello,world\nhello,universe'.encode('utf-8')).decode(),
        'headers': {'Content-Disposition': 'attachment; filename="test.csv"', 'Content-Type': 'application/octet-stream'},
        'isBase64Encoded': True,
        'statusCode': 200}

    assert download_attachment(path="/my/test.csv", headers=sec_fetch_headers) == {  # path has leading '/'
        'body': b64encode('hello,world\nhello,universe'.encode('utf-8')).decode(),
        'headers': {'Content-Disposition': 'attachment; filename="test.csv"', 'Content-Type': 'application/octet-stream'},
        'isBase64Encoded': True,
        'statusCode': 200}

    assert download_attachment(path="some/unknown/object.csv", headers=sec_fetch_headers) == {
        'body': '{"error": "Unable to find the requested object"}',
        'headers': {'Content-Type': 'application/json'},
        'statusCode': 404}

    assert download_attachment(path="some/../dangerous?request/../object.csv", headers=sec_fetch_headers) == {
        'body': '{"error": "Invalid path has been requested"}',
        'headers': {'Content-Type': 'application/json'},
        'statusCode': 400}
