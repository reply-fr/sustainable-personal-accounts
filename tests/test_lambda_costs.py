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


sample_daily_chunk = {
    'GroupDefinitions': [{'Type': 'DIMENSION', 'Key': 'LINKED_ACCOUNT'}],
    'ResultsByTime': [{'TimePeriod': {'Start': '2023-04-07', 'End': '2023-04-08'},
                       'Total': {},
                       'Groups': [{'Keys': ['123456789012'], 'Metrics': {'UnblendedCost': {'Amount': '0.1234', 'Unit': 'USD'}}}],
                       'Estimated': True}],
    'DimensionValueAttributes': [{'Value': '123456789012', 'Attributes': {'description': 'My Account'}}],
    'ResponseMetadata': {'RequestId': '7e93bf36-a74e-4d67-9359-1756a4fcacd6',
                         'HTTPStatusCode': 200,
                         'HTTPHeaders': {'date': 'Sat, 08 Apr 2023 20:49:44 GMT', 'content-type': 'application/x-amz-json-1.1', 'content-length': '368', 'connection': 'keep-alive', 'x-amzn-requestid': '7e93bf36-a74e-4d67-9359-1756a4fcacd6', 'cache-control': 'no-cache'},
                         'RetryAttempts': 0}}


def test_enumerate_daily_cost_per_account():
    mock = Mock()
    mock.client.return_value.get_cost_and_usage.return_value = sample_daily_chunk
    results = {account for account, cost in Costs.enumerate_daily_cost_per_account(session=mock)}
    assert results == {'123456789012'}


sample_monthly_chunk_per_account = {
    'GroupDefinitions': [{'Type': 'DIMENSION', 'Key': 'LINKED_ACCOUNT'}, {'Type': 'DIMENSION', 'Key': 'SERVICE'}],
    'ResultsByTime': [{'TimePeriod': {'Start': '2023-04-01', 'End': '2023-05-01'},
                       'Total': {},
                       'Groups': [{'Keys': ['123456789012', 'AWS CloudTrail'], 'Metrics': {'UnblendedCost': {'Amount': '0', 'Unit': 'USD'}}},
                                  {'Keys': ['123456789012', 'AWS Config'], 'Metrics': {'UnblendedCost': {'Amount': '0.621', 'Unit': 'USD'}}},
                                  {'Keys': ['123456789012', 'AWS Key Management Service'], 'Metrics': {'UnblendedCost': {'Amount': '0.2375000019', 'Unit': 'USD'}}},
                                  {'Keys': ['123456789012', 'AWS Lambda'], 'Metrics': {'UnblendedCost': {'Amount': '0.0007388303', 'Unit': 'USD'}}},
                                  {'Keys': ['123456789012', 'AWS Secrets Manager'], 'Metrics': {'UnblendedCost': {'Amount': '0.1911111092', 'Unit': 'USD'}}},
                                  {'Keys': ['123456789012', 'AWS Systems Manager'], 'Metrics': {'UnblendedCost': {'Amount': '7.03337', 'Unit': 'USD'}}},
                                  {'Keys': ['123456789012', 'AWS X-Ray'], 'Metrics': {'UnblendedCost': {'Amount': '0', 'Unit': 'USD'}}},
                                  {'Keys': ['123456789012', 'Amazon Connect Customer Profiles'], 'Metrics': {'UnblendedCost': {'Amount': '0', 'Unit': 'USD'}}},
                                  {'Keys': ['123456789012', 'Amazon DynamoDB'], 'Metrics': {'UnblendedCost': {'Amount': '0.0012142925', 'Unit': 'USD'}}},
                                  {'Keys': ['123456789012', 'Amazon Kinesis Firehose'], 'Metrics': {'UnblendedCost': {'Amount': '0.00575622', 'Unit': 'USD'}}},
                                  {'Keys': ['123456789012', 'Amazon Simple Notification Service'], 'Metrics': {'UnblendedCost': {'Amount': '0', 'Unit': 'USD'}}},
                                  {'Keys': ['123456789012', 'Amazon Simple Queue Service'], 'Metrics': {'UnblendedCost': {'Amount': '0', 'Unit': 'USD'}}},
                                  {'Keys': ['123456789012', 'Amazon Simple Storage Service'], 'Metrics': {'UnblendedCost': {'Amount': '0.0181906402', 'Unit': 'USD'}}},
                                  {'Keys': ['123456789012', 'AmazonCloudWatch'], 'Metrics': {'UnblendedCost': {'Amount': '2.2405013391', 'Unit': 'USD'}}},
                                  {'Keys': ['123456789012', 'CloudWatch Events'], 'Metrics': {'UnblendedCost': {'Amount': '0.000353', 'Unit': 'USD'}}},
                                  {'Keys': ['123456789012', 'CodeBuild'], 'Metrics': {'UnblendedCost': {'Amount': '0.005', 'Unit': 'USD'}}},
                                  {'Keys': ['123456789012', 'Tax'], 'Metrics': {'UnblendedCost': {'Amount': '2', 'Unit': 'USD'}}}],
                       'Estimated': True}],
    'DimensionValueAttributes': [{'Value': '123456789012', 'Attributes': {'description': 'Automation'}}],
    'ResponseMetadata': {'RequestId': 'bb61aa02-dda7-40b4-a74c-b2edc61ee577',
                         'HTTPStatusCode': 200,
                         'HTTPHeaders': {'date': 'Sat, 08 Apr 2023 21:02:05 GMT', 'content-type': 'application/x-amz-json-1.1', 'content-length': '2166', 'connection': 'keep-alive', 'x-amzn-requestid': 'bb61aa02-dda7-40b4-a74c-b2edc61ee577', 'cache-control': 'no-cache'},
                         'RetryAttempts': 0}}


def test_enumerate_monthly_breakdown_per_account():
    mock = Mock()
    mock.client.return_value.get_cost_and_usage.return_value = sample_monthly_chunk_per_account
    results = {account for account, cost in Costs.enumerate_monthly_breakdown_per_account(session=mock)}
    assert results == {'123456789012'}


sample_monthly_chunk_for_account = {
    'GroupDefinitions': [{'Type': 'DIMENSION', 'Key': 'SERVICE'}],
    'ResultsByTime': [{'TimePeriod': {'Start': '2023-04-01', 'End': '2023-04-08'},
                       'Total': {},
                       'Groups': [{'Keys': ['AWS CloudTrail'], 'Metrics': {'UnblendedCost': {'Amount': '0', 'Unit': 'USD'}}},
                                  {'Keys': ['AWS Config'], 'Metrics': {'UnblendedCost': {'Amount': '0.621', 'Unit': 'USD'}}},
                                  {'Keys': ['AWS Key Management Service'], 'Metrics': {'UnblendedCost': {'Amount': '0.2333333352', 'Unit': 'USD'}}},
                                  {'Keys': ['AWS Lambda'], 'Metrics': {'UnblendedCost': {'Amount': '0.0007335991', 'Unit': 'USD'}}},
                                  {'Keys': ['AWS Secrets Manager'], 'Metrics': {'UnblendedCost': {'Amount': '0.1855555537', 'Unit': 'USD'}}},
                                  {'Keys': ['AWS Systems Manager'], 'Metrics': {'UnblendedCost': {'Amount': '7.029695', 'Unit': 'USD'}}},
                                  {'Keys': ['AWS X-Ray'], 'Metrics': {'UnblendedCost': {'Amount': '0', 'Unit': 'USD'}}},
                                  {'Keys': ['Amazon Connect Customer Profiles'], 'Metrics': {'UnblendedCost': {'Amount': '0', 'Unit': 'USD'}}},
                                  {'Keys': ['Amazon DynamoDB'], 'Metrics': {'UnblendedCost': {'Amount': '0.0012100475', 'Unit': 'USD'}}},
                                  {'Keys': ['Amazon Kinesis Firehose'], 'Metrics': {'UnblendedCost': {'Amount': '0.0055919603', 'Unit': 'USD'}}},
                                  {'Keys': ['Amazon Simple Notification Service'], 'Metrics': {'UnblendedCost': {'Amount': '0', 'Unit': 'USD'}}},
                                  {'Keys': ['Amazon Simple Queue Service'], 'Metrics': {'UnblendedCost': {'Amount': '0', 'Unit': 'USD'}}},
                                  {'Keys': ['Amazon Simple Storage Service'], 'Metrics': {'UnblendedCost': {'Amount': '0.0181478036', 'Unit': 'USD'}}},
                                  {'Keys': ['AmazonCloudWatch'], 'Metrics': {'UnblendedCost': {'Amount': '2.1759910056', 'Unit': 'USD'}}},
                                  {'Keys': ['CloudWatch Events'], 'Metrics': {'UnblendedCost': {'Amount': '0.000351', 'Unit': 'USD'}}},
                                  {'Keys': ['CodeBuild'], 'Metrics': {'UnblendedCost': {'Amount': '0.005', 'Unit': 'USD'}}},
                                  {'Keys': ['Tax'], 'Metrics': {'UnblendedCost': {'Amount': '2', 'Unit': 'USD'}}}],
                       'Estimated': True}],
    'DimensionValueAttributes': [],
    'ResponseMetadata': {'RequestId': '93e000ed-78a1-4a46-8eb6-2da749244e14',
                         'HTTPStatusCode': 200,
                         'HTTPHeaders': {'date': 'Sat, 08 Apr 2023 21:10:05 GMT', 'content-type': 'application/x-amz-json-1.1', 'content-length': '1804', 'connection': 'keep-alive', 'x-amzn-requestid': '93e000ed-78a1-4a46-8eb6-2da749244e14', 'cache-control': 'no-cache'},
                         'RetryAttempts': 0}}


def test_enumerate_monthly_breakdown_for_account():
    mock = Mock()
    mock.client.return_value.get_cost_and_usage.return_value = sample_monthly_chunk_for_account
    results = [item for item in Costs.enumerate_monthly_breakdown_for_account(account='123456789012', session=mock)]
    assert len(results) == 17


sample_breakdown = [
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


@pytest.mark.unit_tests
def test_build_detailed_csv_report():
    report = Costs.build_detailed_csv_report(cost_center="BU", breakdown=sample_breakdown, day=date(2023, 3, 23))
    assert len(report.strip().split('\n')) == 46


@pytest.mark.unit_tests
def test_build_excel_report_for_cost_center():
    report = Costs.build_excel_report_for_cost_center(cost_center="BU", breakdown=sample_breakdown, day=date(2023, 3, 23))
    assert len(report) > 200


@pytest.mark.unit_tests
def test_build_excel_report_for_account():
    report = Costs.build_excel_report_for_account(account='123456789012', breakdown=sample_breakdown, day=date(2023, 3, 23))
    assert len(report) > 200


sample_costs = {
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
def test_build_summary_csv_report():
    report = Costs.build_summary_csv_report(costs=sample_costs, day=date(2023, 3, 23))
    assert len(report.strip().split('\n')) == 9


@pytest.mark.unit_tests
def test_build_summary_excel_report():
    report = Costs.build_summary_excel_report(costs=sample_costs, day=date(2023, 3, 23))
    assert len(report) > 200
