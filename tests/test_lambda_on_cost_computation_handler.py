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

logging.getLogger("botocore").setLevel(logging.CRITICAL)
logging.getLogger("urllib3").setLevel(logging.CRITICAL)

import boto3
from datetime import date
from unittest.mock import Mock, patch
from moto import mock_s3, mock_ses
import os
import pytest

from lambdas.on_cost_computation_handler import (build_charge_reports_per_cost_center,
                                                 build_service_reports_per_cost_center,
                                                 email_reports,
                                                 get_currency_rates,
                                                 get_json_from_url,
                                                 get_report_path,
                                                 store_report)
from tests.test_lambda_costs import sample_accounts, sample_chunk_monthly_charges_per_account, sample_chunk_monthly_services_per_account

# pytestmark = pytest.mark.wip


@pytest.mark.unit_tests
@patch.dict(os.environ, dict(REPORTING_COSTS_PREFIX="costs",
                             REPORTS_BUCKET_NAME="my_bucket"))
@mock_s3
def test_build_charge_reports_per_cost_center():
    s3 = boto3.client("s3")
    s3.create_bucket(Bucket="my_bucket",
                     CreateBucketConfiguration=dict(LocationConstraint='eu-west-3'))

    day = date(2023, 3, 31)
    mock = Mock()
    mock.client.return_value.get_cost_and_usage.return_value = sample_chunk_monthly_charges_per_account
    build_charge_reports_per_cost_center(accounts=sample_accounts, day=day, session=mock)


@pytest.mark.unit_tests
@patch.dict(os.environ, dict(REPORTING_COSTS_PREFIX="costs",
                             REPORTS_BUCKET_NAME="my_bucket"))
@mock_s3
def test_build_service_reports_per_cost_center():
    s3 = boto3.client("s3")
    s3.create_bucket(Bucket="my_bucket",
                     CreateBucketConfiguration=dict(LocationConstraint='eu-west-3'))

    day = date(2023, 3, 31)
    mock = Mock()
    mock.client.return_value.get_cost_and_usage.return_value = sample_chunk_monthly_services_per_account
    build_service_reports_per_cost_center(accounts=sample_accounts, day=day, session=mock)


@pytest.mark.unit_tests
@patch.dict(os.environ, dict(COST_EMAIL_RECIPIENTS='alice@example.com, bob@example.com',
                             ORIGIN_EMAIL_RECIPIENT='costs@example.com',
                             REPORTING_COSTS_PREFIX="costs"))
@mock_s3
@mock_ses
def test_email_reports():
    day = date(2023, 3, 31)
    path = get_report_path(cost_center='Summary', label='services', day=day, suffix='test')

    s3 = boto3.client("s3")
    s3.create_bucket(Bucket="my_bucket",
                     CreateBucketConfiguration=dict(LocationConstraint='eu-west-3'))

    s3.put_object(Bucket="my_bucket",
                  Key=path,
                  Body='hello world!')

    ses = boto3.client('ses')
    ses.verify_email_identity(EmailAddress='costs@example.com')

    assert email_reports(day=day, objects=[f"s3://my_bucket/{path}"]) == '[OK]'


@pytest.mark.unit_tests
@patch.dict(os.environ, dict(ORIGIN_EMAIL_RECIPIENT=''))
def test_email_reports_without_origin_email_recipient():
    day = date(2023, 3, 31)
    assert email_reports(day=day, objects=[]) is None


@pytest.mark.unit_tests
@patch.dict(os.environ, dict(COST_EMAIL_RECIPIENTS='',
                             ORIGIN_EMAIL_RECIPIENT='costs@example.com'))
def test_email_reports_without_cost_email_recipients():
    day = date(2023, 3, 31)
    assert email_reports(day=day, objects=[]) is None


@pytest.mark.integration_tests
def test_get_currency_rates():
    result = get_currency_rates()
    assert result['EUR'] > 0.0


@pytest.mark.integration_tests
def test_get_json_from_url():
    result = get_json_from_url(url="https://open.er-api.com/v6/latest/USD")
    assert result['base_code'] == 'USD'
    assert result['rates']['EUR'] > 0.0


@pytest.mark.unit_tests
@patch.dict(os.environ, dict(REPORTING_COSTS_PREFIX="costs"))
def test_get_report_path():
    result = get_report_path(cost_center='product-a', label='charges', day=date(2023, 3, 25), suffix='xyz')
    assert result == 'costs/product-a/2023-03-product-a-charges.xyz'


@pytest.mark.unit_tests
@patch.dict(os.environ, dict(COST_EMAIL_RECIPIENTS='alice@example.com, bob@example.com',
                             ORIGIN_EMAIL_RECIPIENT='costs@example.com',
                             REPORTS_BUCKET_NAME="my_bucket"))
@mock_s3
def test_store_report():
    s3 = boto3.client("s3")
    s3.create_bucket(Bucket="my_bucket",
                     CreateBucketConfiguration=dict(LocationConstraint='eu-west-3'))
    store_report(path="path/hello.txt", report="hello world") == '[OK]'
