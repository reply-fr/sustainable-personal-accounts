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

from boto3.session import Session
import pytest
from unittest.mock import Mock

from code import get_assumed_session

# pytestmark = pytest.mark.wip


@pytest.fixture
def mock():
    handle = Mock()
    handle.client.return_value.assume_role.return_value = dict(Credentials=dict(AccessKeyId='ak',
                                                                                SecretAccessKey='sk',
                                                                                SessionToken='token'))
    return handle


@pytest.mark.unit_tests
def test_get_assumed_session_minimum(mock):
    session = get_assumed_session(role_arn='arn:aws:iam::222222222222:role/role-on-source-account',
                                  session=mock)
    assert isinstance(session, Session)


@pytest.mark.unit_tests
def test_get_assumed_session_maximum(mock):
    session = get_assumed_session(role_arn='arn:aws:iam::222222222222:role/role-on-source-account',
                                  region='eu-west-12',
                                  name='a-name',
                                  session=mock)
    assert isinstance(session, Session)
    mock.client.assert_called_with('sts')
    mock.client.return_value.assume_role.assert_called_with(
        RoleArn='arn:aws:iam::222222222222:role/role-on-source-account',
        RoleSessionName='a-name')


@pytest.mark.unit_tests
def test_get_assumed_session_invalid_arn():
    with pytest.raises(ValueError):
        get_assumed_session(role_arn='arn')
