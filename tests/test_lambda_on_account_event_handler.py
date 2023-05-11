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
from moto import mock_cloudwatch, mock_dynamodb, mock_events, mock_organizations, mock_s3, mock_ssm
import os
import pytest

from lambdas import Events
from lambdas.on_account_event_handler import (handle_account_event, handle_console_login_event, handle_report, build_report, get_report_path)
from lambdas.key_value_store import KeyValueStore

# pytestmark = pytest.mark.wip
from tests.fixture_key_value_store import create_my_table, populate_shadows_table
from tests.fixture_small_setup import given_a_small_setup


@pytest.mark.integration_tests
@patch.dict(os.environ, dict(ENVIRONMENT_IDENTIFIER="envt1",
                             METERING_SHADOWS_DATASTORE="my_table",
                             VERBOSITY='DEBUG'))
@mock_dynamodb
@mock_cloudwatch
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
                             METERING_SHADOWS_DATASTORE="my_table",
                             VERBOSITY='DEBUG'))
@mock_cloudwatch
@mock_dynamodb
@mock_organizations
def test_handle_preparation_report_event():
    create_my_table()

    event = Events.load_event_from_template(template="fixtures/events/report-event-template.json",
                                            context=dict(account="123456789012",
                                                         label="PreparationReport",
                                                         message="some log",
                                                         environment="envt1"))
    assert handle_account_event(event=event, context=None) == '[OK] PreparationReport 123456789012'


@pytest.mark.unit_tests
@patch.dict(os.environ, dict(ENVIRONMENT_IDENTIFIER="envt1",
                             METERING_SHADOWS_DATASTORE="my_table",
                             VERBOSITY='DEBUG'))
@mock_cloudwatch
@mock_dynamodb
@mock_organizations
def test_handle_purge_report_event():
    create_my_table()

    event = Events.load_event_from_template(template="fixtures/events/report-event-template.json",
                                            context=dict(account="123456789012",
                                                         label="PurgeReport",
                                                         message="some log",
                                                         environment="envt1"))
    assert handle_account_event(event=event, context=None) == '[OK] PurgeReport 123456789012'


@pytest.mark.unit_tests
@patch.dict(os.environ, dict(ENVIRONMENT_IDENTIFIER="envt1",
                             VERBOSITY='INFO'))
def test_handle_account_event_on_unexpected_environment():
    event = Events.load_event_from_template(template="fixtures/events/account-event-template.json",
                                            context=dict(account="123456789012",
                                                         label="CreatedAccount",
                                                         environment="alien*environment"))
    assert handle_account_event(event=event) == "[DEBUG] Unexpected environment 'alien*environment'"


@pytest.mark.integration_tests
@patch.dict(os.environ, dict(ENVIRONMENT_IDENTIFIER="envt1",
                             VERBOSITY='INFO'))
@mock_events
@mock_organizations
@mock_ssm
def test_handle_console_login_event_for_account_root():
    context = given_a_small_setup(environment="envt1")
    event = Events.load_event_from_template(template="fixtures/events/signin-console-login-for-account-root-template.json",
                                            context=dict(account_id=context.alice_account))
    assert handle_console_login_event(event=event) == f"[OK] {context.alice_account}"


@pytest.mark.integration_tests
@patch.dict(os.environ, dict(ENVIRONMENT_IDENTIFIER="envt1",
                             METERING_SHADOWS_DATASTORE="my_table",
                             VERBOSITY='INFO'))
@mock_dynamodb
@mock_events
@mock_organizations
@mock_ssm
def test_handle_console_login_event_for_assumed_role():
    context = given_a_small_setup(environment='envt1')
    create_my_table()

    event = Events.load_event_from_template(template="fixtures/events/signin-console-login-for-assumed-role-template.json",
                                            context=dict(account_id=context.alice_account,
                                                         account_holder="alice@example.com"))
    assert handle_console_login_event(event=event) == f"[OK] {context.alice_account}"

    event = Events.load_event_from_template(template="fixtures/events/signin-console-login-for-assumed-role-template.json",
                                            context=dict(account_id="123456789012",
                                                         account_holder="alice@example.com"))
    assert handle_console_login_event(event=event) == "[DEBUG] No settings could be found for account 123456789012"


@pytest.mark.integration_tests
@patch.dict(os.environ, dict(ENVIRONMENT_IDENTIFIER="envt1",
                             VERBOSITY='INFO'))
@mock_events
@mock_organizations
@mock_ssm
def test_handle_console_login_event_for_iam_user():
    context = given_a_small_setup(environment='envt1')

    event = Events.load_event_from_template(template="fixtures/events/signin-console-login-for-iam-user-template.json",
                                            context=dict(account_id=context.bob_account,
                                                         account_holder="bob"))
    assert handle_console_login_event(event=event) == f"[OK] {context.bob_account}"


@pytest.mark.unit_tests
@patch.dict(os.environ, dict(ENVIRONMENT_IDENTIFIER="envt1",
                             VERBOSITY='INFO'))
def test_handle_console_login_event_for_unknown_identity_type():
    event = Events.load_event_from_template(template="fixtures/events/signin-console-login-for-account-root-template.json",
                                            context=dict(account_id="123456789012"))
    event["detail"]["userIdentity"]["type"] = '*alien*'
    assert handle_console_login_event(event=event) == "[DEBUG] Do not know how to handle identity type '*alien*'"


@pytest.mark.integration_tests
@patch.dict(os.environ, dict(ENVIRONMENT_IDENTIFIER="envt1",
                             METERING_SHADOWS_DATASTORE="my_table",
                             REPORTS_BUCKET_NAME="my_bucket",
                             REPORTING_INVENTORIES_PREFIX="my_inventories",
                             VERBOSITY='INFO'))
@mock_dynamodb
@mock_organizations
@mock_s3
def test_handle_report():
    create_my_table()
    populate_shadows_table()
    s3 = boto3.client("s3")
    s3.create_bucket(Bucket="my_bucket",
                     CreateBucketConfiguration=dict(LocationConstraint='eu-west-3'))
    assert handle_report() == "[OK]"
    response = s3.get_object(Bucket="my_bucket",
                             Key=get_report_path())
    assert response['ContentLength'] > 100
    report = response['Body'].read().decode('utf-8')
    assert report == ("Cost Center,Cost Owner,Organizational Unit,Account,Name,Email,State,Console Login\r\n"
                      "DevOps Tools,bob@example.com,Unknown,222222222222,Alice,alice@example.com,released,2023-03-09T22:13:29\r\n"
                      "Computing Tools,cesar@example.com,Unknown,333333333333,Bob,bob@example.com,released,2023-03-09T22:13:29\r\n"
                      "Tools,alfred@example.com,Unknown,444444444444,César,cesar@example.com,released,2023-03-09T22:13:29\r\n"
                      "Computing Tools,cesar@example.com,Unknown,555555555555,Efoe,efoe@example.com,released,2023-03-09T22:13:29\r\n"
                      "DevOps Tools,bob@example.com,Unknown,666666666666,Francis,francis@example.com,assigned,2023-03-09T22:13:29\r\n"
                      "DevOps Tools,bob@example.com,Unknown,777777777777,Gustav,gustav@example.com,released,2023-03-09T22:13:29\r\n"
                      "DevOps Tools,bob@example.com,Unknown,888888888888,Irène,irene@example.com,released,2023-03-09T22:13:29\r\n"
                      "Reporting Tools,alfred@example.com,Unknown,999999999999,Joe,joe@example.com,purged,2023-03-09T22:13:29\r\n")


@pytest.mark.integration_tests
@patch.dict(os.environ, dict(ENVIRONMENT_IDENTIFIER="envt1",
                             METERING_SHADOWS_DATASTORE="my_table",
                             VERBOSITY='INFO'))
@mock_dynamodb
@mock_organizations
def test_build_report():
    create_my_table()
    populate_shadows_table()
    records = KeyValueStore(table_name="my_table").scan()
    report = build_report(records=records)
    assert len(report.split("\n")) == 10


@pytest.mark.unit_tests
@patch.dict(os.environ, dict(REPORTING_INVENTORIES_PREFIX="all/the/inventories"))
def test_get_report_path():
    key = get_report_path(date(2022, 12, 25))
    assert key == "all/the/inventories/2022/12/2022-12-25-inventory.csv"
    key = get_report_path(date(2023, 1, 2))
    assert key == "all/the/inventories/2023/01/2023-01-02-inventory.csv"
