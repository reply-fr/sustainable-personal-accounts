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

from datetime import date
from unittest.mock import Mock
import pytest

from lambdas.costs import Costs

pytestmark = pytest.mark.wip


sample_breakdown_of_services = [
    {
        "account": "123456789012",
        "service": "AWS CloudTrail",
        "amount": "0",
        "name": "alice@example.com",
        "unit": "Sandboxes",
    },
    {
        "account": "123456789012",
        "service": "AWS Config",
        "amount": "0.16005",
        "name": "alice@example.com",
        "unit": "Sandboxes",
    },
    {
        "account": "123456789012",
        "service": "AWS Key Management Service",
        "amount": "0.00109998",
        "name": "alice@example.com",
        "unit": "Sandboxes",
    },
    {
        "account": "123456789012",
        "service": "AWS Step Functions",
        "amount": "0.0000000036",
        "name": "alice@example.com",
        "unit": "Sandboxes",
    },
    {
        "account": "123456789012",
        "service": "Amazon Simple Notification Service",
        "amount": "0",
        "name": "alice@example.com",
        "unit": "Sandboxes",
    },
    {
        "account": "123456789012",
        "service": "Amazon Simple Queue Service",
        "amount": "0",
        "name": "alice@example.com",
        "unit": "Sandboxes",
    },
    {
        "account": "123456789012",
        "service": "Amazon Simple Storage Service",
        "amount": "0.0015585312",
        "name": "alice@example.com",
        "unit": "Sandboxes",
    },
    {
        "account": "123456789012",
        "service": "Amazon Timestream",
        "amount": "0.00000189",
        "name": "alice@example.com",
        "unit": "Sandboxes",
    },
    {
        "account": "123456789012",
        "service": "AmazonCloudWatch",
        "amount": "0.0000123541",
        "name": "alice@example.com",
        "unit": "Sandboxes",
    },
    {
        "account": "123456789012",
        "service": "CloudWatch Events",
        "amount": "0.00000873",
        "name": "alice@example.com",
        "unit": "Sandboxes",
    },
    {
        "account": "123456789012",
        "service": "CodeBuild",
        "amount": "0.0291",
        "name": "alice@example.com",
        "unit": "Sandboxes",
    },
    {
        "account": "123456789012",
        "service": "Tax",
        "amount": "0.04",
        "name": "alice@example.com",
        "unit": "Sandboxes",
    },
    {
        "account": "456789012345",
        "service": "AWS CloudTrail",
        "amount": "0",
        "name": "bob@example.com",
        "unit": "Sandboxes",
    },
    {
        "account": "456789012345",
        "service": "AWS Config",
        "amount": "0.16005",
        "name": "bob@example.com",
        "unit": "Sandboxes",
    },
    {
        "account": "456789012345",
        "service": "AWS Key Management Service",
        "amount": "0.00097776",
        "name": "bob@example.com",
        "unit": "Sandboxes",
    },
    {
        "account": "456789012345",
        "service": "AWS Step Functions",
        "amount": "0.0000000036",
        "name": "bob@example.com",
        "unit": "Sandboxes",
    },
    {
        "account": "456789012345",
        "service": "Amazon Simple Notification Service",
        "amount": "0",
        "name": "bob@example.com",
        "unit": "Sandboxes",
    },
    {
        "account": "456789012345",
        "service": "Amazon Simple Queue Service",
        "amount": "0",
        "name": "bob@example.com",
        "unit": "Sandboxes",
    },
    {
        "account": "456789012345",
        "service": "Amazon Simple Storage Service",
        "amount": "0.001573474",
        "name": "bob@example.com",
        "unit": "Sandboxes",
    },
    {
        "account": "456789012345",
        "service": "AmazonCloudWatch",
        "amount": "0.0000123521",
        "name": "bob@example.com",
        "unit": "Sandboxes",
    },
    {
        "account": "456789012345",
        "service": "CloudWatch Events",
        "amount": "0.00000873",
        "name": "bob@example.com",
        "unit": "Sandboxes",
    },
    {
        "account": "456789012345",
        "service": "CodeBuild",
        "amount": "0.0291",
        "name": "bob@example.com",
        "unit": "Sandboxes",
    },
    {
        "account": "456789012345",
        "service": "Tax",
        "amount": "0.04",
        "name": "bob@example.com",
        "unit": "Sandboxes",
    },
    {
        "account": "789012345678",
        "service": "AWS CloudTrail",
        "amount": "0",
        "name": "charles@example.com",
        "unit": "Sandboxes",
    },
    {
        "account": "789012345678",
        "service": "AWS CodeArtifact",
        "amount": "0",
        "name": "charles@example.com",
        "unit": "Sandboxes",
    },
    {
        "account": "789012345678",
        "service": "AWS Config",
        "amount": "3.21846",
        "name": "charles@example.com",
        "unit": "Sandboxes",
    },
    {
        "account": "789012345678",
        "service": "AWS Key Management Service",
        "amount": "10.5464810416",
        "name": "charles@example.com",
        "unit": "Sandboxes",
    },
    {
        "account": "789012345678",
        "service": "AWS Lambda",
        "amount": "0",
        "name": "charles@example.com",
        "unit": "Sandboxes",
    },
    {
        "account": "789012345678",
        "service": "AWS Secrets Manager",
        "amount": "0.386675289",
        "name": "charles@example.com",
        "unit": "Sandboxes",
    },
    {
        "account": "789012345678",
        "service": "AWS Step Functions",
        "amount": "0.0000000048",
        "name": "charles@example.com",
        "unit": "Sandboxes",
    },
    {
        "account": "789012345678",
        "service": "Amazon Connect Customer Profiles",
        "amount": "0",
        "name": "charles@example.com",
        "unit": "Sandboxes",
    },
    {
        "account": "789012345678",
        "service": "Amazon DynamoDB",
        "amount": "0.5817672",
        "name": "charles@example.com",
        "unit": "Sandboxes",
    },
    {
        "account": "789012345678",
        "service": "Amazon EC2 Container Registry (ECR)",
        "amount": "0.0002805051",
        "name": "charles@example.com",
        "unit": "Sandboxes",
    },
    {
        "account": "789012345678",
        "service": "EC2 - Other",
        "amount": "10.1037640066",
        "name": "charles@example.com",
        "unit": "Sandboxes",
    },
    {
        "account": "789012345678",
        "service": "Amazon Elastic Compute Cloud - Compute",
        "amount": "4.6803508814",
        "name": "charles@example.com",
        "unit": "Sandboxes",
    },
    {
        "account": "789012345678",
        "service": "Amazon Elastic Container Service for Kubernetes",
        "amount": "7.2094347347",
        "name": "charles@example.com",
        "unit": "Sandboxes",
    },
    {
        "account": "789012345678",
        "service": "Amazon Elastic Load Balancing",
        "amount": "0.048888159",
        "name": "charles@example.com",
        "unit": "Sandboxes",
    },
    {
        "account": "789012345678",
        "service": "Amazon Simple Notification Service",
        "amount": "0",
        "name": "charles@example.com",
        "unit": "Sandboxes",
    },
    {
        "account": "789012345678",
        "service": "Amazon Simple Queue Service",
        "amount": "0",
        "name": "charles@example.com",
        "unit": "Sandboxes",
    },
    {
        "account": "789012345678",
        "service": "Amazon Simple Storage Service",
        "amount": "0.0171990014",
        "name": "charles@example.com",
        "unit": "Sandboxes",
    },
    {
        "account": "789012345678",
        "service": "AmazonCloudWatch",
        "amount": "1.4290028198",
        "name": "charles@example.com",
        "unit": "Sandboxes",
    },
    {
        "account": "789012345678",
        "service": "CloudWatch Events",
        "amount": "0.00002813",
        "name": "charles@example.com",
        "unit": "Sandboxes",
    },
    {
        "account": "789012345678",
        "service": "CodeBuild",
        "amount": "0.1552",
        "name": "charles@example.com",
        "unit": "Sandboxes",
    },
    {
        "account": "789012345678",
        "service": "Tax",
        "amount": "7.68",
        "name": "charles@example.com",
        "unit": "Sandboxes",
    },
]

sample_summary_of_services = {
    "Data": [
        {
            "account": "123456789012",
            "service": "AWS CloudTrail",
            "amount": "0",
            "name": "alice@example.com",
            "unit": "Sandboxes",
        },
        {
            "account": "123456789012",
            "service": "AWS Config",
            "amount": "0.621",
            "name": "alice@example.com",
            "unit": "Sandboxes",
        },
        {
            "account": "123456789012",
            "service": "AWS Key Management Service",
            "amount": "0.000099",
            "name": "alice@example.com",
            "unit": "Sandboxes",
        },
        {
            "account": "210987654321",
            "service": "Amazon Simple Notification Service",
            "amount": "0.1234",
            "name": "production@example.com",
            "unit": "Production",
        },
        {
            "account": "210987654321",
            "service": "Amazon Simple Queue Service",
            "amount": "0.1234",
            "name": "production@example.com",
            "unit": "Production",
        },
    ],
    "Sigma": [
        {
            "account": "456789012345",
            "service": "AWS CloudTrail",
            "amount": "0",
            "name": "quantum-production",
            "unit": "Production",
        },
        {
            "account": "456789012345",
            "service": "AWS Config",
            "amount": "0.20079",
            "name": "quantum-production",
            "unit": "Production",
        },
        {
            "account": "456789012345",
            "service": "AWS Cost Explorer",
            "amount": "0.0097",
            "name": "quantum-production",
            "unit": "Production",
        },
    ],
    "Storm": [
        {
            "account": "789012345678",
            "service": "AWS CloudTrail",
            "amount": "0.2118823545",
            "name": "charles@example.com",
            "unit": "Sandboxes",
        },
        {
            "account": "789012345678",
            "service": "AWS Config",
            "amount": "0.28248",
            "name": "charles@example.com",
            "unit": "Sandboxes",
        },
        {
            "account": "789012345678",
            "service": "AWS Cost Explorer",
            "amount": "0.0088",
            "name": "charles@example.com",
            "unit": "Sandboxes",
        },
    ],
}


@pytest.mark.unit_tests
def test_enumerate_daily_costs_per_account(sample_chunk_daily_costs_per_account):
    mock = Mock()
    mock.client.return_value.get_cost_and_usage.return_value = sample_chunk_daily_costs_per_account
    results = {account for account, cost in Costs.enumerate_daily_costs_per_account(session=mock)}
    assert results == {'123456789012'}


@pytest.mark.unit_tests
def test_enumerate_monthly_costs_for_account(sample_chunk_monthly_costs_for_account):
    mock = Mock()
    mock.client.return_value.get_cost_and_usage.return_value = sample_chunk_monthly_costs_for_account
    results = [item for item in Costs.enumerate_monthly_costs_for_account(account='123456789012', session=mock)]
    assert len(results) == 17


@pytest.mark.unit_tests
def test_enumerate_monthly_charges_per_account(sample_chunk_monthly_charges_per_account):
    mock = Mock()
    mock.client.return_value.get_cost_and_usage.return_value = sample_chunk_monthly_charges_per_account
    results = {account for account, _ in Costs.enumerate_monthly_charges_per_account(session=mock)}
    assert results == {'123456789012', '456789012345', '789012345678', '012345678901', '345678901234'}


@pytest.mark.unit_tests
def test_enumerate_monthly_services_per_account(sample_chunk_monthly_services_per_account):
    mock = Mock()
    mock.client.return_value.get_cost_and_usage.return_value = sample_chunk_monthly_services_per_account
    results = {account for account, cost in Costs.enumerate_monthly_services_per_account(session=mock)}
    assert results == {'123456789012'}


@pytest.mark.unit_tests
def test_get_charges_per_cost_center(sample_chunk_monthly_charges_per_account, sample_accounts):
    mock = Mock()
    mock.client.return_value.get_cost_and_usage.return_value = sample_chunk_monthly_charges_per_account
    charges = Costs.get_charges_per_cost_center(accounts=sample_accounts, session=mock)
    assert charges == {'Product A': [{'account': '123456789012', 'charge': 'Solution Provider Program Discount', 'amount': '-0.8038363727', 'name': 'alice@example.com', 'unit': 'Committed'},
                                     {'account': '123456789012', 'charge': 'Tax', 'amount': '5.19', 'name': 'alice@example.com', 'unit': 'Committed'},
                                     {'account': '123456789012', 'charge': 'Usage', 'amount': '26.7945452638', 'name': 'alice@example.com', 'unit': 'Committed'},
                                     {'account': '012345678901', 'charge': 'Support', 'amount': '1.0368862512', 'name': 'david@example.com', 'unit': 'Non-Committed'},
                                     {'account': '012345678901', 'charge': 'Tax', 'amount': '0.24', 'name': 'david@example.com', 'unit': 'Non-Committed'},
                                     {'account': '012345678901', 'charge': 'Usage', 'amount': '1.2295395649', 'name': 'david@example.com', 'unit': 'Non-Committed'}],
                       'Product B': [{'account': '456789012345', 'charge': 'Solution Provider Program Discount', 'amount': '-0.0167705004', 'name': 'bob@example.com', 'unit': 'Committed'},
                                     {'account': '456789012345', 'charge': 'Tax', 'amount': '0.11', 'name': 'bob@example.com', 'unit': 'Committed'},
                                     {'account': '456789012345', 'charge': 'Usage', 'amount': '0.5590172084', 'name': 'bob@example.com', 'unit': 'Committed'}],
                       'Product C': [{'account': '789012345678', 'charge': 'Solution Provider Program Discount', 'amount': '-0.6905270498', 'name': 'charles@reply.com', 'unit': 'Committed'},
                                     {'account': '789012345678', 'charge': 'Tax', 'amount': '4.46', 'name': 'charles@reply.com', 'unit': 'Committed'},
                                     {'account': '789012345678', 'charge': 'Usage', 'amount': '23.0175687783', 'name': 'charles@reply.com', 'unit': 'Committed'},
                                     {'account': '345678901234', 'charge': 'Solution Provider Program Discount', 'amount': '-0.0356584397', 'name': 'estelle@example.com', 'unit': 'Non-Committed'},
                                     {'account': '345678901234', 'charge': 'Tax', 'amount': '0.23', 'name': 'estelle@example.com', 'unit': 'Non-Committed'},
                                     {'account': '345678901234', 'charge': 'Usage', 'amount': '1.1886139495', 'name': 'estelle@example.com', 'unit': 'Non-Committed'}]}


@pytest.mark.unit_tests
def test_get_services_per_cost_center(sample_chunk_monthly_services_per_account, sample_accounts):
    mock = Mock()
    mock.client.return_value.get_cost_and_usage.return_value = sample_chunk_monthly_services_per_account
    services = Costs.get_services_per_cost_center(accounts=sample_accounts, session=mock)
    print(services)
    assert services == {'Product A': [{'account': '123456789012', 'service': 'AWS CloudTrail', 'amount': '0', 'name': 'alice@example.com', 'unit': 'Committed'},
                                      {'account': '123456789012', 'service': 'AWS Config', 'amount': '0.621', 'name': 'alice@example.com', 'unit': 'Committed'},
                                      {'account': '123456789012', 'service': 'AWS Key Management Service', 'amount': '0.2375000019', 'name': 'alice@example.com', 'unit': 'Committed'},
                                      {'account': '123456789012', 'service': 'AWS Lambda', 'amount': '0.0007388303', 'name': 'alice@example.com', 'unit': 'Committed'},
                                      {'account': '123456789012', 'service': 'AWS Secrets Manager', 'amount': '0.1911111092', 'name': 'alice@example.com', 'unit': 'Committed'},
                                      {'account': '123456789012', 'service': 'AWS Systems Manager', 'amount': '7.03337', 'name': 'alice@example.com', 'unit': 'Committed'},
                                      {'account': '123456789012', 'service': 'AWS X-Ray', 'amount': '0', 'name': 'alice@example.com', 'unit': 'Committed'},
                                      {'account': '123456789012', 'service': 'Amazon Connect Customer Profiles', 'amount': '0', 'name': 'alice@example.com', 'unit': 'Committed'},
                                      {'account': '123456789012', 'service': 'Amazon DynamoDB', 'amount': '0.0012142925', 'name': 'alice@example.com', 'unit': 'Committed'},
                                      {'account': '123456789012', 'service': 'Amazon Kinesis Firehose', 'amount': '0.00575622', 'name': 'alice@example.com', 'unit': 'Committed'},
                                      {'account': '123456789012', 'service': 'Amazon Simple Notification Service', 'amount': '0', 'name': 'alice@example.com', 'unit': 'Committed'},
                                      {'account': '123456789012', 'service': 'Amazon Simple Queue Service', 'amount': '0', 'name': 'alice@example.com', 'unit': 'Committed'},
                                      {'account': '123456789012', 'service': 'Amazon Simple Storage Service', 'amount': '0.0181906402', 'name': 'alice@example.com', 'unit': 'Committed'},
                                      {'account': '123456789012', 'service': 'AmazonCloudWatch', 'amount': '2.2405013391', 'name': 'alice@example.com', 'unit': 'Committed'},
                                      {'account': '123456789012', 'service': 'CloudWatch Events', 'amount': '0.000353', 'name': 'alice@example.com', 'unit': 'Committed'},
                                      {'account': '123456789012', 'service': 'CodeBuild', 'amount': '0.005', 'name': 'alice@example.com', 'unit': 'Committed'},
                                      {'account': '123456789012', 'service': 'Tax', 'amount': '2', 'name': 'alice@example.com', 'unit': 'Committed'}]}


@pytest.mark.unit_tests
def test_build_breakdown_of_costs_excel_report_for_account():
    report = Costs.build_breakdown_of_costs_excel_report_for_account(account='123456789012', breakdown=sample_breakdown_of_services, day=date(2023, 3, 23))
    assert len(report) > 200


@pytest.mark.unit_tests
def test_build_breakdown_of_services_csv_report_for_cost_center():
    report = Costs.build_breakdown_of_services_csv_report_for_cost_center(cost_center="BU", breakdown=sample_breakdown_of_services, day=date(2023, 3, 23))
    assert len(report.strip().split('\n')) == 46


@pytest.mark.unit_tests
def test_build_breakdown_of_services_excel_report_for_cost_center():
    report = Costs.build_breakdown_of_services_excel_report_for_cost_center(cost_center="BU", breakdown=sample_breakdown_of_services, day=date(2023, 3, 23))
    assert len(report) > 200


@pytest.mark.unit_tests
def test_build_summary_of_charges_csv_report(sample_chunk_monthly_charges_per_account, sample_accounts):
    mock = Mock()
    mock.client.return_value.get_cost_and_usage.return_value = sample_chunk_monthly_charges_per_account
    charges = Costs.get_charges_per_cost_center(accounts=sample_accounts, session=mock)
    report = Costs.build_summary_of_charges_csv_report(charges=charges, day=date(2023, 3, 31))
    assert len(report) > 200
    lines = report.split('\n', 2)
    assert lines[0].strip() == 'Month,Cost Center,Organizational Unit,Account,Charges (USD),Solution Provider Program Discount (USD),Support (USD),Tax (USD),Usage (USD)'
    assert lines[1].strip() == '2023-03,Product A,Committed,alice@example.com (123456789012),31.1807088911,-0.8038363727,,5.19,26.7945452638'


@pytest.mark.unit_tests
def test_build_summary_of_charges_excel_report(sample_chunk_monthly_charges_per_account, sample_accounts):
    mock = Mock()
    mock.client.return_value.get_cost_and_usage.return_value = sample_chunk_monthly_charges_per_account
    charges = Costs.get_charges_per_cost_center(accounts=sample_accounts, session=mock)
    report = Costs.build_summary_of_charges_excel_report(charges=charges, day=date(2023, 3, 31))
    assert len(report) > 200


@pytest.mark.unit_tests
def test_build_summary_of_services_csv_report():
    report = Costs.build_summary_of_services_csv_report(costs=sample_summary_of_services, day=date(2023, 3, 23))
    assert len(report.strip().split('\n')) == 9


@pytest.mark.unit_tests
def test_build_summary_of_services_excel_report():
    report = Costs.build_summary_of_services_excel_report(costs=sample_summary_of_services, day=date(2023, 3, 23))
    assert len(report) > 200
