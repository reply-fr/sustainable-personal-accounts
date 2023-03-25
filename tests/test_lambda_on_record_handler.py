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
from datetime import date
import json
from unittest.mock import patch
from moto import mock_dynamodb, mock_s3
import os
import pytest

from lambdas import Events, KeyValueStore
from lambdas.on_record_handler import build_reports, handle_record, handle_monthly_reporting, handle_daily_reporting, get_hashes, get_report_key

# pytestmark = pytest.mark.wip
from tests.fixture_key_value_store import create_my_table, populate_records_table


sample_payload = json.dumps(
    {"account-state": "released",
     "cost-owner": "bob@acme.com",
     "account-holder": "alice@acme.com",
     "cost-center": "Tools",
     "transaction": "on-boarding",
     "account": "123456789012",
     "begin": 1678652493.1665454,
     "identifier": "2a446cb7-6eef-4691-bf32-957404be1598",
     "end": 1678652621.5461018,
     "duration": 128.3795564174652})


@pytest.mark.integration_tests
@patch.dict(os.environ, dict(ENVIRONMENT_IDENTIFIER="envt1",
                             METERING_RECORDS_DATASTORE="my_table",
                             VERBOSITY='DEBUG'))
@mock_dynamodb
def test_store_end_report():
    create_my_table()

    event = Events.load_event_from_template(template="fixtures/events/spa-event-template.json",
                                            context=dict(label='SuccessfulMaintenanceEvent',
                                                         payload=sample_payload,
                                                         content_type='application.json',
                                                         environment="envt1"))
    assert handle_record(event=event, context=None) == "[OK] SuccessfulMaintenanceEvent"
    records = KeyValueStore(table_name="my_table").scan()
    reports = build_reports(records=records)
    assert list(reports.keys()) == ['Tools']


@pytest.mark.unit_tests
@patch.dict(os.environ, dict(ENVIRONMENT_IDENTIFIER="envt1",
                             METERING_RECORDS_DATASTORE="my_table",
                             VERBOSITY='DEBUG'))
@mock_dynamodb
def test_handle_record():
    create_my_table()

    for label in Events.RECORD_EVENT_LABELS:
        event = Events.load_event_from_template(template="fixtures/events/spa-event-template.json",
                                                context=dict(payload=sample_payload,
                                                             label=label,
                                                             environment="envt1"))
        assert handle_record(event=event, context=None) == f"[OK] {label}"


@pytest.mark.unit_tests
@patch.dict(os.environ, dict(ENVIRONMENT_IDENTIFIER="envt1",
                             VERBOSITY='INFO'))
def test_handle_record_on_unexpected_environment():
    event = Events.load_event_from_template(template="fixtures/events/spa-event-template.json",
                                            context=dict(payload=sample_payload,
                                                         label="CreatedAccount",
                                                         environment="alien*environment"))
    assert handle_record(event=event, context=None) == "[DEBUG] Unexpected environment 'alien*environment'"


@pytest.mark.unit_tests
@patch.dict(os.environ, dict(ENVIRONMENT_IDENTIFIER="envt1",
                             METERING_RECORDS_DATASTORE="my_table",
                             REPORTS_BUCKET_NAME="my_bucket",
                             REPORTING_ACTIVITIES_PREFIX="my_activities",
                             VERBOSITY='INFO'))
@mock_dynamodb
@mock_s3
def test_handle_monthly_reporting():
    create_my_table()
    populate_records_table()
    s3 = boto3.client("s3")
    s3.create_bucket(Bucket="my_bucket",
                     CreateBucketConfiguration=dict(LocationConstraint=s3.meta.region_name))
    assert handle_monthly_reporting(day=date(year=2023, month=4, day=20)) == "[OK]"
    response = s3.get_object(Bucket="my_bucket",
                             Key=get_report_key(label="DevOps Tools"))
    assert response['ContentLength'] > 100
    report = response['Body'].read().decode('utf-8')
    assert len(report.split("\n")) == 20


@pytest.mark.unit_tests
@patch.dict(os.environ, dict(ENVIRONMENT_IDENTIFIER="envt1",
                             METERING_RECORDS_DATASTORE="my_table",
                             REPORTS_BUCKET_NAME="my_bucket",
                             REPORTING_ACTIVITIES_PREFIX="my_activities",
                             VERBOSITY='INFO'))
@mock_dynamodb
@mock_s3
def test_handle_daily_reporting():
    create_my_table()
    populate_records_table()
    s3 = boto3.client("s3")
    s3.create_bucket(Bucket="my_bucket",
                     CreateBucketConfiguration=dict(LocationConstraint=s3.meta.region_name))
    assert handle_daily_reporting(day=date(year=2023, month=3, day=30)) == "[OK]"
    response = s3.get_object(Bucket="my_bucket",
                             Key=get_report_key(label="DevOps Tools"))
    assert response['ContentLength'] > 100
    report = response['Body'].read().decode('utf-8')
    assert len(report.split("\n")) == 20


@pytest.mark.unit_tests
@patch.dict(os.environ, dict(ENVIRONMENT_IDENTIFIER="envt1",
                             METERING_RECORDS_DATASTORE="my_table",
                             VERBOSITY='INFO'))
@mock_dynamodb
def test_build_reports():
    create_my_table()
    populate_records_table()
    records = KeyValueStore(table_name="my_table").scan()
    reports = build_reports(records=records)
    assert list(reports.keys()) == ['DevOps Tools', 'Computing Tools', 'Tools', 'Reporting Tools']


@pytest.mark.unit_tests
def test_get_hashes():
    hashes = get_hashes(date(2022, 12, 25))
    assert hashes == ['2022-12-01', '2022-12-02', '2022-12-03', '2022-12-04', '2022-12-05',
                      '2022-12-06', '2022-12-07', '2022-12-08', '2022-12-09', '2022-12-10',
                      '2022-12-11', '2022-12-12', '2022-12-13', '2022-12-14', '2022-12-15',
                      '2022-12-16', '2022-12-17', '2022-12-18', '2022-12-19', '2022-12-20',
                      '2022-12-21', '2022-12-22', '2022-12-23', '2022-12-24', '2022-12-25']
    hashes = get_hashes(date(2023, 1, 2))
    assert hashes == ['2023-01-01', '2023-01-02']


@pytest.mark.unit_tests
@patch.dict(os.environ, dict(REPORTING_ACTIVITIES_PREFIX="all/the/activities"))
def test_get_report_key():
    key = get_report_key("CostCenterOne", date(2022, 12, 25))
    assert key == "all/the/activities/CostCenterOne/2022-12-CostCenterOne-activities.csv"
    key = get_report_key("CostCenterTwo", date(2023, 1, 2))
    assert key == "all/the/activities/CostCenterTwo/2023-01-CostCenterTwo-activities.csv"
