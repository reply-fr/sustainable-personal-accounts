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

import pytest


@pytest.fixture
def sample_accounts():
    return {
        "123456789012": {
            "name": "alice@example.com",
            "unit_name": "Committed",
            "tags": {"cost-center": "Product A"},
        },
        "456789012345": {
            "name": "bob@example.com",
            "unit_name": "Committed",
            "tags": {"cost-center": "Product B"},
        },
        "789012345678": {
            "name": "charles@reply.com",
            "unit_name": "Committed",
            "tags": {"cost-center": "Product C"},
        },
        "012345678901": {
            "name": "david@example.com",
            "unit_name": "Non-Committed",
            "tags": {"cost-center": "Product A"},
        },
        "345678901234": {
            "name": "estelle@example.com",
            "unit_name": "Non-Committed",
            "tags": {"cost-center": "Product C"},
        },
    }


@pytest.fixture
def sample_chunk_daily_costs_per_account():
    return {
        "GroupDefinitions": [{"Type": "DIMENSION", "Key": "LINKED_ACCOUNT"}],
        "ResultsByTime": [
            {
                "TimePeriod": {"Start": "2023-04-07", "End": "2023-04-08"},
                "Total": {},
                "Groups": [
                    {
                        "Keys": ["123456789012"],
                        "Metrics": {
                            "UnblendedCost": {"Amount": "0.1234", "Unit": "USD"}
                        },
                    }
                ],
                "Estimated": True,
            }
        ],
        "DimensionValueAttributes": [
            {"Value": "123456789012", "Attributes": {"description": "My Account"}}
        ],
        "ResponseMetadata": {
            "RequestId": "7e93bf36-a74e-4d67-9359-1756a4fcacd6",
            "HTTPStatusCode": 200,
            "HTTPHeaders": {
                "date": "Sat, 08 Apr 2023 20:49:44 GMT",
                "content-type": "application/x-amz-json-1.1",
                "content-length": "368",
                "connection": "keep-alive",
                "x-amzn-requestid": "7e93bf36-a74e-4d67-9359-1756a4fcacd6",
                "cache-control": "no-cache",
            },
            "RetryAttempts": 0,
        },
    }


@pytest.fixture
def sample_chunk_monthly_costs_for_account():
    return {
        "GroupDefinitions": [{"Type": "DIMENSION", "Key": "SERVICE"}],
        "ResultsByTime": [
            {
                "TimePeriod": {"Start": "2023-04-01", "End": "2023-04-08"},
                "Total": {},
                "Groups": [
                    {
                        "Keys": ["AWS CloudTrail"],
                        "Metrics": {"UnblendedCost": {"Amount": "0", "Unit": "USD"}},
                    },
                    {
                        "Keys": ["AWS Config"],
                        "Metrics": {
                            "UnblendedCost": {"Amount": "0.621", "Unit": "USD"}
                        },
                    },
                    {
                        "Keys": ["AWS Key Management Service"],
                        "Metrics": {
                            "UnblendedCost": {"Amount": "0.2333333352", "Unit": "USD"}
                        },
                    },
                    {
                        "Keys": ["AWS Lambda"],
                        "Metrics": {
                            "UnblendedCost": {"Amount": "0.0007335991", "Unit": "USD"}
                        },
                    },
                    {
                        "Keys": ["AWS Secrets Manager"],
                        "Metrics": {
                            "UnblendedCost": {"Amount": "0.1855555537", "Unit": "USD"}
                        },
                    },
                    {
                        "Keys": ["AWS Systems Manager"],
                        "Metrics": {
                            "UnblendedCost": {"Amount": "7.029695", "Unit": "USD"}
                        },
                    },
                    {
                        "Keys": ["AWS X-Ray"],
                        "Metrics": {"UnblendedCost": {"Amount": "0", "Unit": "USD"}},
                    },
                    {
                        "Keys": ["Amazon Connect Customer Profiles"],
                        "Metrics": {"UnblendedCost": {"Amount": "0", "Unit": "USD"}},
                    },
                    {
                        "Keys": ["Amazon DynamoDB"],
                        "Metrics": {
                            "UnblendedCost": {"Amount": "0.0012100475", "Unit": "USD"}
                        },
                    },
                    {
                        "Keys": ["Amazon Kinesis Firehose"],
                        "Metrics": {
                            "UnblendedCost": {"Amount": "0.0055919603", "Unit": "USD"}
                        },
                    },
                    {
                        "Keys": ["Amazon Simple Notification Service"],
                        "Metrics": {"UnblendedCost": {"Amount": "0", "Unit": "USD"}},
                    },
                    {
                        "Keys": ["Amazon Simple Queue Service"],
                        "Metrics": {"UnblendedCost": {"Amount": "0", "Unit": "USD"}},
                    },
                    {
                        "Keys": ["Amazon Simple Storage Service"],
                        "Metrics": {
                            "UnblendedCost": {"Amount": "0.0181478036", "Unit": "USD"}
                        },
                    },
                    {
                        "Keys": ["AmazonCloudWatch"],
                        "Metrics": {
                            "UnblendedCost": {"Amount": "2.1759910056", "Unit": "USD"}
                        },
                    },
                    {
                        "Keys": ["CloudWatch Events"],
                        "Metrics": {
                            "UnblendedCost": {"Amount": "0.000351", "Unit": "USD"}
                        },
                    },
                    {
                        "Keys": ["CodeBuild"],
                        "Metrics": {
                            "UnblendedCost": {"Amount": "0.005", "Unit": "USD"}
                        },
                    },
                    {
                        "Keys": ["Tax"],
                        "Metrics": {"UnblendedCost": {"Amount": "2", "Unit": "USD"}},
                    },
                ],
                "Estimated": True,
            }
        ],
        "DimensionValueAttributes": [],
        "ResponseMetadata": {
            "RequestId": "93e000ed-78a1-4a46-8eb6-2da749244e14",
            "HTTPStatusCode": 200,
            "HTTPHeaders": {
                "date": "Sat, 08 Apr 2023 21:10:05 GMT",
                "content-type": "application/x-amz-json-1.1",
                "content-length": "1804",
                "connection": "keep-alive",
                "x-amzn-requestid": "93e000ed-78a1-4a46-8eb6-2da749244e14",
                "cache-control": "no-cache",
            },
            "RetryAttempts": 0,
        },
    }


@pytest.fixture
def sample_chunk_monthly_charges_per_account():
    return {
        "GroupDefinitions": [
            {"Type": "DIMENSION", "Key": "LINKED_ACCOUNT"},
            {"Type": "DIMENSION", "Key": "RECORD_TYPE"},
        ],
        "ResultsByTime": [
            {
                "TimePeriod": {"Start": "2023-03-01", "End": "2023-04-01"},
                "Total": {},
                "Groups": [
                    {
                        "Keys": ["123456789012", "Solution Provider Program Discount"],
                        "Metrics": {
                            "UnblendedCost": {"Amount": "-0.8038363727", "Unit": "USD"}
                        },
                    },
                    {
                        "Keys": ["123456789012", "Tax"],
                        "Metrics": {"UnblendedCost": {"Amount": "5.19", "Unit": "USD"}},
                    },
                    {
                        "Keys": ["123456789012", "Usage"],
                        "Metrics": {
                            "UnblendedCost": {"Amount": "26.7945452638", "Unit": "USD"}
                        },
                    },
                    {
                        "Keys": ["456789012345", "Solution Provider Program Discount"],
                        "Metrics": {
                            "UnblendedCost": {"Amount": "-0.0167705004", "Unit": "USD"}
                        },
                    },
                    {
                        "Keys": ["456789012345", "Tax"],
                        "Metrics": {"UnblendedCost": {"Amount": "0.11", "Unit": "USD"}},
                    },
                    {
                        "Keys": ["456789012345", "Usage"],
                        "Metrics": {
                            "UnblendedCost": {"Amount": "0.5590172084", "Unit": "USD"}
                        },
                    },
                    {
                        "Keys": ["789012345678", "Solution Provider Program Discount"],
                        "Metrics": {
                            "UnblendedCost": {"Amount": "-0.6905270498", "Unit": "USD"}
                        },
                    },
                    {
                        "Keys": ["789012345678", "Tax"],
                        "Metrics": {"UnblendedCost": {"Amount": "4.46", "Unit": "USD"}},
                    },
                    {
                        "Keys": ["789012345678", "Usage"],
                        "Metrics": {
                            "UnblendedCost": {"Amount": "23.0175687783", "Unit": "USD"}
                        },
                    },
                    {
                        "Keys": ["012345678901", "Support"],
                        "Metrics": {
                            "UnblendedCost": {"Amount": "1.0368862512", "Unit": "USD"}
                        },
                    },
                    {
                        "Keys": ["012345678901", "Tax"],
                        "Metrics": {"UnblendedCost": {"Amount": "0.24", "Unit": "USD"}},
                    },
                    {
                        "Keys": ["012345678901", "Usage"],
                        "Metrics": {
                            "UnblendedCost": {"Amount": "1.2295395649", "Unit": "USD"}
                        },
                    },
                    {
                        "Keys": ["345678901234", "Solution Provider Program Discount"],
                        "Metrics": {
                            "UnblendedCost": {"Amount": "-0.0356584397", "Unit": "USD"}
                        },
                    },
                    {
                        "Keys": ["345678901234", "Tax"],
                        "Metrics": {"UnblendedCost": {"Amount": "0.23", "Unit": "USD"}},
                    },
                    {
                        "Keys": ["345678901234", "Usage"],
                        "Metrics": {
                            "UnblendedCost": {"Amount": "1.1886139495", "Unit": "USD"}
                        },
                    },
                ],
                "Estimated": False,
            }
        ],
        "DimensionValueAttributes": [
            {
                "Value": "123456789012",
                "Attributes": {"description": "alice@example.com"},
            },
            {
                "Value": "456789012345",
                "Attributes": {"description": "bob@example.com"}},
            {
                "Value": "789012345678",
                "Attributes": {"description": "charles@reply.com"},
            },
            {
                "Value": "012345678901",
                "Attributes": {"description": "david@example.com"},
            },
            {
                "Value": "345678901234",
                "Attributes": {"description": "estelle@example.com"},
            },
        ],
        "ResponseMetadata": {
            "RequestId": "ab34a27c-18f3-4ad9-a5e2-6f93b9e2a80f",
            "HTTPStatusCode": 200,
            "HTTPHeaders": {
                "date": "Wed, 12 Apr 2023 20:10:21 GMT",
                "content-type": "application/x-amz-json-1.1",
                "content-length": "23622",
                "connection": "keep-alive",
                "cache-control": "no-cache",
            },
            "RetryAttempts": 0,
        },
    }


@pytest.fixture
def sample_chunk_monthly_services_per_account():
    return {
        "GroupDefinitions": [
            {"Type": "DIMENSION", "Key": "LINKED_ACCOUNT"},
            {"Type": "DIMENSION", "Key": "SERVICE"},
        ],
        "ResultsByTime": [
            {
                "TimePeriod": {"Start": "2023-04-01", "End": "2023-05-01"},
                "Total": {},
                "Groups": [
                    {
                        "Keys": ["123456789012", "AWS CloudTrail"],
                        "Metrics": {"UnblendedCost": {"Amount": "0", "Unit": "USD"}},
                    },
                    {
                        "Keys": ["123456789012", "AWS Config"],
                        "Metrics": {
                            "UnblendedCost": {"Amount": "0.621", "Unit": "USD"}
                        },
                    },
                    {
                        "Keys": ["123456789012", "AWS Key Management Service"],
                        "Metrics": {
                            "UnblendedCost": {"Amount": "0.2375000019", "Unit": "USD"}
                        },
                    },
                    {
                        "Keys": ["123456789012", "AWS Lambda"],
                        "Metrics": {
                            "UnblendedCost": {"Amount": "0.0007388303", "Unit": "USD"}
                        },
                    },
                    {
                        "Keys": ["123456789012", "AWS Secrets Manager"],
                        "Metrics": {
                            "UnblendedCost": {"Amount": "0.1911111092", "Unit": "USD"}
                        },
                    },
                    {
                        "Keys": ["123456789012", "AWS Systems Manager"],
                        "Metrics": {
                            "UnblendedCost": {"Amount": "7.03337", "Unit": "USD"}
                        },
                    },
                    {
                        "Keys": ["123456789012", "AWS X-Ray"],
                        "Metrics": {"UnblendedCost": {"Amount": "0", "Unit": "USD"}},
                    },
                    {
                        "Keys": ["123456789012", "Amazon Connect Customer Profiles"],
                        "Metrics": {"UnblendedCost": {"Amount": "0", "Unit": "USD"}},
                    },
                    {
                        "Keys": ["123456789012", "Amazon DynamoDB"],
                        "Metrics": {
                            "UnblendedCost": {"Amount": "0.0012142925", "Unit": "USD"}
                        },
                    },
                    {
                        "Keys": ["123456789012", "Amazon Kinesis Firehose"],
                        "Metrics": {
                            "UnblendedCost": {"Amount": "0.00575622", "Unit": "USD"}
                        },
                    },
                    {
                        "Keys": ["123456789012", "Amazon Simple Notification Service"],
                        "Metrics": {"UnblendedCost": {"Amount": "0", "Unit": "USD"}},
                    },
                    {
                        "Keys": ["123456789012", "Amazon Simple Queue Service"],
                        "Metrics": {"UnblendedCost": {"Amount": "0", "Unit": "USD"}},
                    },
                    {
                        "Keys": ["123456789012", "Amazon Simple Storage Service"],
                        "Metrics": {
                            "UnblendedCost": {"Amount": "0.0181906402", "Unit": "USD"}
                        },
                    },
                    {
                        "Keys": ["123456789012", "AmazonCloudWatch"],
                        "Metrics": {
                            "UnblendedCost": {"Amount": "2.2405013391", "Unit": "USD"}
                        },
                    },
                    {
                        "Keys": ["123456789012", "CloudWatch Events"],
                        "Metrics": {
                            "UnblendedCost": {"Amount": "0.000353", "Unit": "USD"}
                        },
                    },
                    {
                        "Keys": ["123456789012", "CodeBuild"],
                        "Metrics": {
                            "UnblendedCost": {"Amount": "0.005", "Unit": "USD"}
                        },
                    },
                    {
                        "Keys": ["123456789012", "Tax"],
                        "Metrics": {"UnblendedCost": {"Amount": "2", "Unit": "USD"}},
                    },
                ],
                "Estimated": True,
            }
        ],
        "DimensionValueAttributes": [
            {"Value": "123456789012", "Attributes": {"description": "Automation"}}
        ],
        "ResponseMetadata": {
            "RequestId": "bb61aa02-dda7-40b4-a74c-b2edc61ee577",
            "HTTPStatusCode": 200,
            "HTTPHeaders": {
                "date": "Sat, 08 Apr 2023 21:02:05 GMT",
                "content-type": "application/x-amz-json-1.1",
                "content-length": "2166",
                "connection": "keep-alive",
                "x-amzn-requestid": "bb61aa02-dda7-40b4-a74c-b2edc61ee577",
                "cache-control": "no-cache",
            },
            "RetryAttempts": 0,
        },
    }


@pytest.fixture
def sample_chunk_monthly_usages_per_account():
    return {
        "GroupDefinitions": [
            {"Type": "DIMENSION", "Key": "LINKED_ACCOUNT"},
            {"Type": "DIMENSION", "Key": "USAGE_TYPE"},
        ],
        "ResultsByTime": [
            {
                "TimePeriod": {"Start": "2023-04-01", "End": "2023-05-01"},
                "Total": {},
                "Groups": [
                    {
                        "Keys": ["123456789012", "EU-EBS:VolumeUsage.gp3"],
                        "Metrics": {"UnblendedCost": {"Amount": "0", "Unit": "USD"}},
                    },
                    {
                        "Keys": ["123456789012", "EUW3-DataTransfer-Out-Bytes"],
                        "Metrics": {
                            "UnblendedCost": {"Amount": "0.621", "Unit": "USD"}
                        },
                    },
                    {
                        "Keys": ["123456789012", "EU-BoxUsage:r6a.2xlarge"],
                        "Metrics": {
                            "UnblendedCost": {"Amount": "0.2375000019", "Unit": "USD"}
                        },
                    },
                    {
                        "Keys": ["123456789012", "EUW3-TimedStorage-INT-FA-ByteHrs"],
                        "Metrics": {
                            "UnblendedCost": {"Amount": "0.0007388303", "Unit": "USD"}
                        },
                    },
                    {
                        "Keys": ["123456789012", "EUW3-Airflow-SmallEnvironment"],
                        "Metrics": {
                            "UnblendedCost": {"Amount": "0.1911111092", "Unit": "USD"}
                        },
                    },
                    {
                        "Keys": ["123456789012", "EUC1-VpcEndpoint-Hours"],
                        "Metrics": {
                            "UnblendedCost": {"Amount": "7.03337", "Unit": "USD"}
                        },
                    },
                    {
                        "Keys": ["123456789012", "EUW3-Endpoint-Hour"],
                        "Metrics": {"UnblendedCost": {"Amount": "0", "Unit": "USD"}},
                    },
                    {
                        "Keys": ["123456789012", "EU-NatGateway-Hours"],
                        "Metrics": {"UnblendedCost": {"Amount": "0", "Unit": "USD"}},
                    },
                    {
                        "Keys": ["123456789012", "EUW3-ResolverNetworkInterface"],
                        "Metrics": {
                            "UnblendedCost": {"Amount": "0.0012142925", "Unit": "USD"}
                        },
                    },
                    {
                        "Keys": ["123456789012", "USE1-KendraDeveloperEdition"],
                        "Metrics": {
                            "UnblendedCost": {"Amount": "0.00575622", "Unit": "USD"}
                        },
                    },
                    {
                        "Keys": ["123456789012", "QS-User-Enterprise-Month"],
                        "Metrics": {"UnblendedCost": {"Amount": "0", "Unit": "USD"}},
                    },
                    {
                        "Keys": ["123456789012", "EUW3-CloudWAN-CoreNetworkEdge-Hours"],
                        "Metrics": {"UnblendedCost": {"Amount": "0", "Unit": "USD"}},
                    },
                    {
                        "Keys": ["123456789012", "EUW3-TimedStorage-ByteHrs"],
                        "Metrics": {
                            "UnblendedCost": {"Amount": "0.0181906402", "Unit": "USD"}
                        },
                    },
                    {
                        "Keys": ["123456789012", "APS1-CloudWAN-CoreNetworkEdge-Hours"],
                        "Metrics": {
                            "UnblendedCost": {"Amount": "2.2405013391", "Unit": "USD"}
                        },
                    },
                    {
                        "Keys": ["123456789012", "EUW3-BoxUsage:m5.xlarge"],
                        "Metrics": {
                            "UnblendedCost": {"Amount": "0.000353", "Unit": "USD"}
                        },
                    },
                    {
                        "Keys": ["123456789012", "EUC1-Redshift:ServerlessUsage"],
                        "Metrics": {
                            "UnblendedCost": {"Amount": "0.005", "Unit": "USD"}
                        },
                    },
                    {
                        "Keys": ["123456789012", "EUW3-Traffic-GB-Processed"],
                        "Metrics": {"UnblendedCost": {"Amount": "2", "Unit": "USD"}},
                    },
                ],
                "Estimated": True,
            }
        ],
        "DimensionValueAttributes": [
            {"Value": "123456789012", "Attributes": {"description": "Automation"}}
        ],
        "ResponseMetadata": {
            "RequestId": "bb61aa02-dda7-40b4-a74c-b2edc61ee577",
            "HTTPStatusCode": 200,
            "HTTPHeaders": {
                "date": "Sat, 08 Apr 2023 21:02:05 GMT",
                "content-type": "application/x-amz-json-1.1",
                "content-length": "2166",
                "connection": "keep-alive",
                "x-amzn-requestid": "bb61aa02-dda7-40b4-a74c-b2edc61ee577",
                "cache-control": "no-cache",
            },
            "RetryAttempts": 0,
        },
    }
