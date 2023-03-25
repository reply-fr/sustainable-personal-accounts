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
from unittest.mock import patch
import os
import pytest

from lambdas.on_cost_computation_handler import (
    build_detailed_csv_report,
    build_detailed_excel_report,
    build_summary_csv_report,
    build_summary_excel_report,
    get_report_key,
)

pytestmark = pytest.mark.wip


sample_breakdown = [
    {
        "account": "123456789012",
        "service": "AWS CloudTrail",
        "amount": "0",
        "name": "alice@example.com",
        "unit": "ou-hello-world",
    },
    {
        "account": "123456789012",
        "service": "AWS Config",
        "amount": "0.16005",
        "name": "alice@example.com",
        "unit": "ou-hello-world",
    },
    {
        "account": "123456789012",
        "service": "AWS Key Management Service",
        "amount": "0.00109998",
        "name": "alice@example.com",
        "unit": "ou-hello-world",
    },
    {
        "account": "123456789012",
        "service": "AWS Step Functions",
        "amount": "0.0000000036",
        "name": "alice@example.com",
        "unit": "ou-hello-world",
    },
    {
        "account": "123456789012",
        "service": "Amazon Simple Notification Service",
        "amount": "0",
        "name": "alice@example.com",
        "unit": "ou-hello-world",
    },
    {
        "account": "123456789012",
        "service": "Amazon Simple Queue Service",
        "amount": "0",
        "name": "alice@example.com",
        "unit": "ou-hello-world",
    },
    {
        "account": "123456789012",
        "service": "Amazon Simple Storage Service",
        "amount": "0.0015585312",
        "name": "alice@example.com",
        "unit": "ou-hello-world",
    },
    {
        "account": "123456789012",
        "service": "Amazon Timestream",
        "amount": "0.00000189",
        "name": "alice@example.com",
        "unit": "ou-hello-world",
    },
    {
        "account": "123456789012",
        "service": "AmazonCloudWatch",
        "amount": "0.0000123541",
        "name": "alice@example.com",
        "unit": "ou-hello-world",
    },
    {
        "account": "123456789012",
        "service": "CloudWatch Events",
        "amount": "0.00000873",
        "name": "alice@example.com",
        "unit": "ou-hello-world",
    },
    {
        "account": "123456789012",
        "service": "CodeBuild",
        "amount": "0.0291",
        "name": "alice@example.com",
        "unit": "ou-hello-world",
    },
    {
        "account": "123456789012",
        "service": "Tax",
        "amount": "0.04",
        "name": "alice@example.com",
        "unit": "ou-hello-world",
    },
    {
        "account": "456789012345",
        "service": "AWS CloudTrail",
        "amount": "0",
        "name": "bob@example.com",
        "unit": "ou-hello-world",
    },
    {
        "account": "456789012345",
        "service": "AWS Config",
        "amount": "0.16005",
        "name": "bob@example.com",
        "unit": "ou-hello-world",
    },
    {
        "account": "456789012345",
        "service": "AWS Key Management Service",
        "amount": "0.00097776",
        "name": "bob@example.com",
        "unit": "ou-hello-world",
    },
    {
        "account": "456789012345",
        "service": "AWS Step Functions",
        "amount": "0.0000000036",
        "name": "bob@example.com",
        "unit": "ou-hello-world",
    },
    {
        "account": "456789012345",
        "service": "Amazon Simple Notification Service",
        "amount": "0",
        "name": "bob@example.com",
        "unit": "ou-hello-world",
    },
    {
        "account": "456789012345",
        "service": "Amazon Simple Queue Service",
        "amount": "0",
        "name": "bob@example.com",
        "unit": "ou-hello-world",
    },
    {
        "account": "456789012345",
        "service": "Amazon Simple Storage Service",
        "amount": "0.001573474",
        "name": "bob@example.com",
        "unit": "ou-hello-world",
    },
    {
        "account": "456789012345",
        "service": "AmazonCloudWatch",
        "amount": "0.0000123521",
        "name": "bob@example.com",
        "unit": "ou-hello-world",
    },
    {
        "account": "456789012345",
        "service": "CloudWatch Events",
        "amount": "0.00000873",
        "name": "bob@example.com",
        "unit": "ou-hello-world",
    },
    {
        "account": "456789012345",
        "service": "CodeBuild",
        "amount": "0.0291",
        "name": "bob@example.com",
        "unit": "ou-hello-world",
    },
    {
        "account": "456789012345",
        "service": "Tax",
        "amount": "0.04",
        "name": "bob@example.com",
        "unit": "ou-hello-world",
    },
    {
        "account": "789012345678",
        "service": "AWS CloudTrail",
        "amount": "0",
        "name": "charles@example.com",
        "unit": "ou-hello-world",
    },
    {
        "account": "789012345678",
        "service": "AWS CodeArtifact",
        "amount": "0",
        "name": "charles@example.com",
        "unit": "ou-hello-world",
    },
    {
        "account": "789012345678",
        "service": "AWS Config",
        "amount": "3.21846",
        "name": "charles@example.com",
        "unit": "ou-hello-world",
    },
    {
        "account": "789012345678",
        "service": "AWS Key Management Service",
        "amount": "10.5464810416",
        "name": "charles@example.com",
        "unit": "ou-hello-world",
    },
    {
        "account": "789012345678",
        "service": "AWS Lambda",
        "amount": "0",
        "name": "charles@example.com",
        "unit": "ou-hello-world",
    },
    {
        "account": "789012345678",
        "service": "AWS Secrets Manager",
        "amount": "0.386675289",
        "name": "charles@example.com",
        "unit": "ou-hello-world",
    },
    {
        "account": "789012345678",
        "service": "AWS Step Functions",
        "amount": "0.0000000048",
        "name": "charles@example.com",
        "unit": "ou-hello-world",
    },
    {
        "account": "789012345678",
        "service": "Amazon Connect Customer Profiles",
        "amount": "0",
        "name": "charles@example.com",
        "unit": "ou-hello-world",
    },
    {
        "account": "789012345678",
        "service": "Amazon DynamoDB",
        "amount": "0.5817672",
        "name": "charles@example.com",
        "unit": "ou-hello-world",
    },
    {
        "account": "789012345678",
        "service": "Amazon EC2 Container Registry (ECR)",
        "amount": "0.0002805051",
        "name": "charles@example.com",
        "unit": "ou-hello-world",
    },
    {
        "account": "789012345678",
        "service": "EC2 - Other",
        "amount": "10.1037640066",
        "name": "charles@example.com",
        "unit": "ou-hello-world",
    },
    {
        "account": "789012345678",
        "service": "Amazon Elastic Compute Cloud - Compute",
        "amount": "4.6803508814",
        "name": "charles@example.com",
        "unit": "ou-hello-world",
    },
    {
        "account": "789012345678",
        "service": "Amazon Elastic Container Service for Kubernetes",
        "amount": "7.2094347347",
        "name": "charles@example.com",
        "unit": "ou-hello-world",
    },
    {
        "account": "789012345678",
        "service": "Amazon Elastic Load Balancing",
        "amount": "0.048888159",
        "name": "charles@example.com",
        "unit": "ou-hello-world",
    },
    {
        "account": "789012345678",
        "service": "Amazon Simple Notification Service",
        "amount": "0",
        "name": "charles@example.com",
        "unit": "ou-hello-world",
    },
    {
        "account": "789012345678",
        "service": "Amazon Simple Queue Service",
        "amount": "0",
        "name": "charles@example.com",
        "unit": "ou-hello-world",
    },
    {
        "account": "789012345678",
        "service": "Amazon Simple Storage Service",
        "amount": "0.0171990014",
        "name": "charles@example.com",
        "unit": "ou-hello-world",
    },
    {
        "account": "789012345678",
        "service": "AmazonCloudWatch",
        "amount": "1.4290028198",
        "name": "charles@example.com",
        "unit": "ou-hello-world",
    },
    {
        "account": "789012345678",
        "service": "CloudWatch Events",
        "amount": "0.00002813",
        "name": "charles@example.com",
        "unit": "ou-hello-world",
    },
    {
        "account": "789012345678",
        "service": "CodeBuild",
        "amount": "0.1552",
        "name": "charles@example.com",
        "unit": "ou-hello-world",
    },
    {
        "account": "789012345678",
        "service": "Tax",
        "amount": "7.68",
        "name": "charles@example.com",
        "unit": "ou-hello-world",
    },
]


@pytest.mark.unit_tests
def test_build_detailed_csv_report():
    report = build_detailed_csv_report(cost_center="BU", breakdown=sample_breakdown, day=date(2023, 3, 23))
    assert len(report.strip().split('\n')) == 46


@pytest.mark.unit_tests
def test_build_detailed_excel_report():
    report = build_detailed_excel_report(cost_center="BU", breakdown=sample_breakdown, day=date(2023, 3, 23))
    assert len(report) > 200


sample_costs = {
    "Data": [
        {
            "account": "123456789012",
            "service": "AWS CloudTrail",
            "amount": "0",
            "name": "alice@example.com",
            "unit": "ou-hello-word",
        },
        {
            "account": "123456789012",
            "service": "AWS Config",
            "amount": "0.621",
            "name": "alice@example.com",
            "unit": "ou-hello-word",
        },
        {
            "account": "123456789012",
            "service": "AWS Key Management Service",
            "amount": "0.000099",
            "name": "alice@example.com",
            "unit": "ou-hello-word",
        },
        {
            "account": "123456789012",
            "service": "Amazon Simple Notification Service",
            "amount": "0",
            "name": "alice@example.com",
            "unit": "ou-hello-word",
        },
        {
            "account": "123456789012",
            "service": "Amazon Simple Queue Service",
            "amount": "0",
            "name": "alice@example.com",
            "unit": "ou-hello-word",
        },
    ],
    "Sigma": [
        {
            "account": "456789012345",
            "service": "AWS CloudTrail",
            "amount": "0",
            "name": "quatum-production",
            "unit": "ou-hello-universe",
        },
        {
            "account": "456789012345",
            "service": "AWS Config",
            "amount": "0.20079",
            "name": "quatum-production",
            "unit": "ou-hello-universe",
        },
        {
            "account": "456789012345",
            "service": "AWS Cost Explorer",
            "amount": "0.0097",
            "name": "quatum-production",
            "unit": "ou-hello-universe",
        },
    ],
    "Storm": [
        {
            "account": "789012345678",
            "service": "AWS CloudTrail",
            "amount": "0.2118823545",
            "name": "charles@example.com",
            "unit": "ou-hello-moon",
        },
        {
            "account": "789012345678",
            "service": "AWS Config",
            "amount": "0.28248",
            "name": "charles@example.com",
            "unit": "ou-hello-moon",
        },
        {
            "account": "789012345678",
            "service": "AWS Cost Explorer",
            "amount": "0.0088",
            "name": "charles@example.com",
            "unit": "ou-hello-moon",
        },
    ],
}


@pytest.mark.unit_tests
def test_build_summary_csv_report():
    report = build_summary_csv_report(costs=sample_costs, day=date(2023, 3, 23))
    assert len(report.strip().split('\n')) == 5


@pytest.mark.unit_tests
def test_build_summary_excel_report():
    report = build_summary_excel_report(costs=sample_costs, day=date(2023, 3, 23))
    assert len(report) > 200


@pytest.mark.unit_tests
@patch.dict(os.environ, dict(REPORTING_COSTS_PREFIX="costs"))
def test_get_report_key():
    result = get_report_key(label='test', day=date(2023, 3, 25), suffix='xyz')
    assert result == 'costs/test/2023-03-test-costs.xyz'
