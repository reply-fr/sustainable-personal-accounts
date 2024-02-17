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

from moto import mock_aws
import pytest
from types import SimpleNamespace

from lambdas.check_accounts_handler import handle_event, validate_tags

# pytestmark = pytest.mark.wip
from account import Account  # visible from monkeypatch


@pytest.mark.integration_tests
@mock_aws
def test_handle_event(monkeypatch, given_a_small_setup):
    context = given_a_small_setup()

    processed = set()

    def process(account, *arg, **kwargs):
        processed.add(account)
        return SimpleNamespace(id=account, tags={'account-holder': 'a@b.com', 'account-state': 'released'})

    monkeypatch.setattr(Account, 'describe', process)

    result = handle_event()
    assert result == '[OK]'
    assert processed == {context.crm_account, context.erp_account, context.alice_account, context.bob_account, '210987654321'}


@pytest.mark.unit_tests
def test_validate_tags():
    valid_tags = SimpleNamespace(id='123456789012',
                                 tags={'account-holder': 'a@b.com', 'account-state': 'released'})
    validate_tags(item=valid_tags)


@pytest.mark.unit_tests
def test_validate_tags_on_absent_holder():
    absent_holder = SimpleNamespace(id='123456789012',
                                    tags={'account-state': 'released'})
    with pytest.raises(ValueError):
        validate_tags(item=absent_holder)


@pytest.mark.unit_tests
def test_validate_tags_on_invalid_holder():
    invalid_holder = SimpleNamespace(id='123456789012',
                                     tags={'account-holder': 'a_b.com', 'account-state': 'released'})
    with pytest.raises(ValueError):
        validate_tags(item=invalid_holder)


@pytest.mark.unit_tests
def test_validate_tags_on_absent_state():
    absent_state = SimpleNamespace(id='123456789012',
                                   tags={'account-holder': 'a@b.com'})
    with pytest.raises(ValueError):
        validate_tags(item=absent_state)


@pytest.mark.unit_tests
def test_validate_tags_on_invalid_state():
    invalid_state = SimpleNamespace(id='123456789012',
                                    tags={'account-holder': 'a@b.com', 'account-state': '*alien*'})
    with pytest.raises(ValueError):
        validate_tags(item=invalid_state)
