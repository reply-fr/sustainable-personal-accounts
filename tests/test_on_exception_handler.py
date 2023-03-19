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

import boto3
import json
from unittest.mock import Mock, patch
from moto import mock_s3, mock_ssm, mock_sts
import os
import pytest

from code import Events
from code.on_exception_handler import handle_exception, handle_attachment_request, build_csv_report, download_attachment

pytestmark = pytest.mark.wip


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
@mock_s3
@mock_ssm
@mock_sts
def test_handle_exception():

    s3 = boto3.client("s3")
    s3.create_bucket(Bucket="my_bucket",
                     CreateBucketConfiguration=dict(LocationConstraint=s3.meta.region_name))

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


@pytest.mark.integration_tests
@patch.dict(os.environ, dict(ENVIRONMENT_IDENTIFIER="envt1",
                             REPORTING_EXCEPTIONS_PREFIX="exceptions",
                             REPORTS_BUCKET_NAME="my_bucket"))
@mock_s3
def test_handle_attachment_request():

    s3 = boto3.client("s3")
    s3.create_bucket(Bucket="my_bucket",
                     CreateBucketConfiguration=dict(LocationConstraint=s3.meta.region_name))
    s3.put_object(Bucket="my_bucket", Key="exceptions/my/test.csv", Body="hello,world\nhello,universe")

    assert handle_attachment_request(event=dict(rawPath="/my/test.csv")) == {
        'body': 'hello,world\nhello,universe',
        'headers': {'Content-Disposition': 'attachment; filename="test.csv"', 'Content-Type': 'text/csv'},
        'statusCode': 200}


@pytest.mark.unit_tests
def test_build_csv_report():
    sample_report = {'GroupDefinitions': [{'Type': 'DIMENSION', 'Key': 'SERVICE'}],
                     'ResultsByTime': [{'TimePeriod': {'Start': '2023-03-01', 'End': '2023-03-18'},
                                        'Total': {},
                                        'Groups': [{'Keys': ['AWS CloudTrail'], 'Metrics': {'UnblendedCost': {'Amount': '0', 'Unit': 'USD'}}},
                                                   {'Keys': ['AWS Config'], 'Metrics': {'UnblendedCost': {'Amount': '3.3', 'Unit': 'USD'}}},
                                                   {'Keys': ['AWS Key Management Service'], 'Metrics': {'UnblendedCost': {'Amount': '0.5392304', 'Unit': 'USD'}}},
                                                   {'Keys': ['AWS Lambda'], 'Metrics': {'UnblendedCost': {'Amount': '0.0011515946', 'Unit': 'USD'}}},
                                                   {'Keys': ['AWS Secrets Manager'], 'Metrics': {'UnblendedCost': {'Amount': '0.4311827888', 'Unit': 'USD'}}},
                                                   {'Keys': ['AWS Step Functions'], 'Metrics': {'UnblendedCost': {'Amount': '0', 'Unit': 'USD'}}},
                                                   {'Keys': ['AWS Systems Manager'], 'Metrics': {'UnblendedCost': {'Amount': '4.73157601', 'Unit': 'USD'}}},
                                                   {'Keys': ['AWS X-Ray'], 'Metrics': {'UnblendedCost': {'Amount': '0', 'Unit': 'USD'}}},
                                                   {'Keys': ['Amazon Connect Customer Profiles'], 'Metrics': {'UnblendedCost': {'Amount': '0', 'Unit': 'USD'}}},
                                                   {'Keys': ['Amazon DynamoDB'], 'Metrics': {'UnblendedCost': {'Amount': '0.006810086', 'Unit': 'USD'}}},
                                                   {'Keys': ['Amazon Kinesis Firehose'], 'Metrics': {'UnblendedCost': {'Amount': '0.011183841', 'Unit': 'USD'}}},
                                                   {'Keys': ['Amazon Simple Notification Service'], 'Metrics': {'UnblendedCost': {'Amount': '0', 'Unit': 'USD'}}},
                                                   {'Keys': ['Amazon Simple Queue Service'], 'Metrics': {'UnblendedCost': {'Amount': '0', 'Unit': 'USD'}}},
                                                   {'Keys': ['Amazon Simple Storage Service'], 'Metrics': {'UnblendedCost': {'Amount': '0.0153292873', 'Unit': 'USD'}}},
                                                   {'Keys': ['AmazonCloudWatch'], 'Metrics': {'UnblendedCost': {'Amount': '3.8806672007', 'Unit': 'USD'}}},
                                                   {'Keys': ['CloudWatch Events'], 'Metrics': {'UnblendedCost': {'Amount': '0.002184', 'Unit': 'USD'}}},
                                                   {'Keys': ['CodeBuild'], 'Metrics': {'UnblendedCost': {'Amount': '0.04', 'Unit': 'USD'}}},
                                                   {'Keys': ['Tax'], 'Metrics': {'UnblendedCost': {'Amount': '2.5', 'Unit': 'USD'}}}],
                                        'Estimated': True}],
                     'DimensionValueAttributes': [],
                     'ResponseMetadata': {'RequestId': '502805d4-bdc5-4e71-96b4-241ea3230bb1',
                                          'HTTPStatusCode': 200,
                                          'HTTPHeaders': {'date': 'Sat, 18 Mar 2023 06:44:55 GMT',
                                                          'content-type': 'application/x-amz-json-1.1',
                                                          'content-length': '1888',
                                                          'connection': 'keep-alive',
                                                          'x-amzn-requestid': '502805d4-bdc5-4e71-96b4-241ea3230bb1',
                                                          'cache-control': 'no-cache'},
                                          'RetryAttempts': 0}}

    assert build_csv_report(cost_and_usage=sample_report) == ('Start,End,Service,Amount (USD)\r\n'
                                                              '2023-03-01,2023-03-18,AWS CloudTrail,0\r\n'
                                                              '2023-03-01,2023-03-18,AWS Config,3.3\r\n'
                                                              '2023-03-01,2023-03-18,AWS Key Management Service,0.5392304\r\n'
                                                              '2023-03-01,2023-03-18,AWS Lambda,0.0011515946\r\n'
                                                              '2023-03-01,2023-03-18,AWS Secrets Manager,0.4311827888\r\n'
                                                              '2023-03-01,2023-03-18,AWS Step Functions,0\r\n'
                                                              '2023-03-01,2023-03-18,AWS Systems Manager,4.73157601\r\n'
                                                              '2023-03-01,2023-03-18,AWS X-Ray,0\r\n'
                                                              '2023-03-01,2023-03-18,Amazon Connect Customer Profiles,0\r\n'
                                                              '2023-03-01,2023-03-18,Amazon DynamoDB,0.006810086\r\n'
                                                              '2023-03-01,2023-03-18,Amazon Kinesis Firehose,0.011183841\r\n'
                                                              '2023-03-01,2023-03-18,Amazon Simple Notification Service,0\r\n'
                                                              '2023-03-01,2023-03-18,Amazon Simple Queue Service,0\r\n'
                                                              '2023-03-01,2023-03-18,Amazon Simple Storage Service,0.0153292873\r\n'
                                                              '2023-03-01,2023-03-18,AmazonCloudWatch,3.8806672007\r\n'
                                                              '2023-03-01,2023-03-18,CloudWatch Events,0.002184\r\n'
                                                              '2023-03-01,2023-03-18,CodeBuild,0.04\r\n'
                                                              '2023-03-01,2023-03-18,Tax,2.5\r\n')


@pytest.mark.integration_tests
@patch.dict(os.environ, dict(ENVIRONMENT_IDENTIFIER="envt1",
                             REPORTING_EXCEPTIONS_PREFIX="exceptions",
                             REPORTS_BUCKET_NAME="my_bucket"))
@mock_s3
def test_download_attachment():

    s3 = boto3.client("s3")
    s3.create_bucket(Bucket="my_bucket",
                     CreateBucketConfiguration=dict(LocationConstraint=s3.meta.region_name))
    s3.put_object(Bucket="my_bucket", Key="exceptions/my/test.csv", Body="hello,world\nhello,universe")

    assert download_attachment(path="my/test.csv") == {
        'body': 'hello,world\nhello,universe',
        'headers': {'Content-Disposition': 'attachment; filename="test.csv"', 'Content-Type': 'text/csv'},
        'statusCode': 200}

    assert download_attachment(path="/my/test.csv") == {  # path has leading '/'
        'body': 'hello,world\nhello,universe',
        'headers': {'Content-Disposition': 'attachment; filename="test.csv"', 'Content-Type': 'text/csv'},
        'statusCode': 200}

    assert download_attachment(path="some/unknown/object.csv") == {
        'body': '{"error": "Unable to find the requested object"}',
        'headers': {'Content-Type': 'application/json'},
        'statusCode': 404}

    assert download_attachment(path="some/../dangerous?request/../object.csv") == {
        'body': '{"error": "Invalid path has been requested"}',
        'headers': {'Content-Type': 'application/json'},
        'statusCode': 400}
