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

import pytest
from unittest.mock import Mock
from types import SimpleNamespace


from code import Account, State


# pytestmark = pytest.mark.wip


def test_move_to_vanilla():
    client = Mock()
    Account.move(account='0123456789012',
                 state=State.VANILLA,
                 client=client)
    client.tag_resource.assert_called_with(ResourceId='0123456789012', Tags=[{'Key': 'account:state', 'Value': 'vanilla'}])


def test_move_to_assigned():
    client = Mock()
    Account.move(account='0123456789012',
                 state=State.ASSIGNED,
                 client=client)
    client.tag_resource.assert_called_with(ResourceId='0123456789012', Tags=[{'Key': 'account:state', 'Value': 'assigned'}])


def test_move_to_released():
    client = Mock()
    Account.move(account='0123456789012',
                 state=State.RELEASED,
                 client=client)
    client.tag_resource.assert_called_with(ResourceId='0123456789012', Tags=[{'Key': 'account:state', 'Value': 'released'}])


def test_move_to_expired():
    client = Mock()
    Account.move(account='0123456789012',
                 state=State.EXPIRED,
                 client=client)
    client.tag_resource.assert_called_with(ResourceId='0123456789012', Tags=[{'Key': 'account:state', 'Value': 'expired'}])


def test_move_with_exception():
    with pytest.raises(ValueError):
        Account.move(account='0123456789012',
                     state=SimpleNamespace(value='*something*'))
