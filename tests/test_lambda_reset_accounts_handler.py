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

from moto import mock_organizations, mock_ssm
import pytest

from lambdas.reset_accounts_handler import handle_event

# pytestmark = pytest.mark.wip
from account import Account  # visible from monkeypatch


@pytest.mark.integration_tests
@mock_organizations
@mock_ssm
def test_handle_event(given_a_small_setup, monkeypatch):
    context = given_a_small_setup()

    processed = set()

    def process(account, *arg, **kwargs):
        processed.add(account)

    monkeypatch.setattr(Account, 'set_state', process)

    assert handle_event() == '[OK]'
    assert processed == {context.erp_account, context.alice_account, context.bob_account}
