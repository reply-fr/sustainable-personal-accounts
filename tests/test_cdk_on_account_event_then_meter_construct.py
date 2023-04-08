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

from aws_cdk import Stack
from aws_cdk.assertions import Template
import pytest

from cdk import Configuration
from cdk.on_account_event_then_meter_construct import OnAccountEventThenMeter
from cdk.serverless_stack import ServerlessStack

# pytestmark = pytest.mark.wip


@pytest.mark.unit_tests
def test_dynamodb_encryption():
    Configuration.initialize()
    stack = Stack()
    OnAccountEventThenMeter(scope=stack, id='my_construct', parameters=ServerlessStack.get_parameters())
    template = Template.from_stack(stack)
    template.has_resource_properties(
        "AWS::DynamoDB::Table",
        dict(SSESpecification=dict(SSEEnabled=True)))


@pytest.mark.unit_tests
def test_resources_count():
    Configuration.initialize()
    stack = Stack()
    OnAccountEventThenMeter(scope=stack, id='my_construct', parameters=ServerlessStack.get_parameters())
    template = Template.from_stack(stack)
    template.resource_count_is("AWS::DynamoDB::Table", 1)
