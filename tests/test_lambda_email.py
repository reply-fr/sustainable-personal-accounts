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

import boto3
from unittest.mock import patch
from moto import mock_ses
import os
import pytest

from lambdas import Email

pytestmark = pytest.mark.wip


@pytest.mark.unit_tests
@patch.dict(os.environ, dict(ORIGIN_EMAIL_RECIPIENT='alice@example.com'))
@mock_ses
def test_send():
    ses = boto3.client('ses')
    ses.verify_email_identity(EmailAddress='alice@example.com')
    parameters = dict(recipients=['bob@example.com'], subject='my subject', text='my message')
    assert Email.send(**parameters) == '[OK]'
