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
from unittest.mock import patch
from moto import mock_dynamodb, mock_organizations, mock_s3
import os
import pytest

from lambdas import Events
from lambdas.on_account_event_then_shadow_handler import handle_account_event, handle_reporting, build_report, get_report_key
from lambdas.key_value_store import KeyValueStore

from tests.fixture_key_value_store import create_my_table, populate_shadows_table
# pytestmark = pytest.mark.wip


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
    record = instance.retrieve(hash="123456789012")
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


@pytest.mark.unit_tests
@patch.dict(os.environ, dict(ENVIRONMENT_IDENTIFIER="envt1",
                             METERING_SHADOWS_DATASTORE="my_table",
                             REPORTS_BUCKET_NAME="my_bucket",
                             REPORTING_INVENTORIES_PREFIX="my_inventories",
                             VERBOSITY='INFO'))
@mock_dynamodb
@mock_s3
def test_handle_reporting():
    create_my_table()
    populate_shadows_table()
    s3 = boto3.client("s3")
    s3.create_bucket(Bucket="my_bucket",
                     CreateBucketConfiguration=dict(LocationConstraint=s3.meta.region_name))
    assert handle_reporting() == "[OK]"
    response = s3.get_object(Bucket="my_bucket",
                             Key=get_report_key())
    assert response['ContentLength'] > 100
    report = response['Body'].read().decode('utf-8')
    assert len(report.split("\n")) == 10


@pytest.mark.unit_tests
@patch.dict(os.environ, dict(ENVIRONMENT_IDENTIFIER="envt1",
                             METERING_SHADOWS_DATASTORE="my_table",
                             VERBOSITY='INFO'))
@mock_dynamodb
def test_build_report():
    create_my_table()
    populate_shadows_table()
    records = KeyValueStore(table_name="my_table").scan()
    report = build_report(records=records)
    assert len(report.split("\n")) == 10


@pytest.mark.unit_tests
@patch.dict(os.environ, dict(REPORTING_INVENTORIES_PREFIX="all/the/inventories"))
def test_get_report_key():
    key = get_report_key(date(2022, 12, 25))
    assert key == "all/the/inventories/2022/12/2022-12-25-inventory.csv"
    key = get_report_key(date(2023, 1, 2))
    assert key == "all/the/inventories/2023/01/2023-01-02-inventory.csv"
