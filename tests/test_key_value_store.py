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
from moto import mock_dynamodb
import pytest

from code import KeyValueStore

from tests.fixture_key_value_store import create_my_table
pytestmark = pytest.mark.wip


@pytest.mark.unit_tests
@mock_dynamodb
def test_key_value_store():
    create_my_table()

    store = KeyValueStore(table_name='my_table')
    store.remember(key='a', value=dict(hello='world'))
    store.remember(key='b', value=dict(life='is good'))
    assert store.retrieve(key='a') == dict(hello='world')
    assert store.retrieve(key='b') == dict(life='is good')

    store.remember(key='a', value=dict(hello='universe'))
    assert store.retrieve(key='a') == dict(hello='universe')
    assert store.retrieve(key='b') == dict(life='is good')

    store.forget(key='a')
    store.forget(key='a')  # accept unknown key
    assert not store.retrieve(key='a')
    assert store.retrieve(key='b') == dict(life='is good')

    store.remember(key='b', value=dict(life='is short'))
    assert not store.retrieve(key='a')
    assert store.retrieve(key='b') == dict(life='is short')

    store.remember(key='a', value=dict(hello='world'))
    store.remember(key='b', value=dict(life='is good'))
    result = boto3.client('dynamodb').scan(TableName='my_table',
                                           Select='ALL_ATTRIBUTES')
    assert len(result['Items']) == 2
