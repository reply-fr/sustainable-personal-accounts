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

pytestmark = pytest.mark.wip


@pytest.fixture
def test_this_store():

    def store_tester(store):
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

    return store_tester


@pytest.mark.unit_tests
@mock_dynamodb
def test_dynamodb_key_value_store(test_this_store):
    boto3.client('dynamodb').create_table(TableName='my_table',
                                          KeySchema=[dict(AttributeName='Identifier', KeyType='HASH')],
                                          AttributeDefinitions=[dict(AttributeName='Identifier', AttributeType='S')],
                                          BillingMode='PAY_PER_REQUEST')
    boto3.client('dynamodb').get_waiter('table_exists').wait(TableName='my_table')

    store = KeyValueStore.get_instance(path='dynamodb://my_table', cache=False)
    test_this_store(store)

    store.remember(key='a', value=dict(hello='world'))
    store.remember(key='b', value=dict(life='is good'))
    result = boto3.client('dynamodb').scan(TableName='my_table',
                                           Select='ALL_ATTRIBUTES')
    assert len(result['Items']) == 2


@pytest.mark.unit_tests
def test_memory_key_value_store(test_this_store):
    store = KeyValueStore.get_instance(path='memory:', cache=False)
    test_this_store(store)


@pytest.mark.unit_tests
def test_key_value_store_singleton():
    store1 = KeyValueStore.get_instance(path='memory:', cache=False)
    store2 = KeyValueStore.get_instance(path='memory:')
    assert store1 == store2


@pytest.mark.unit_tests
def test_key_value_store_on_unknown_path():
    with pytest.raises(AttributeError):
        KeyValueStore.get_instance(path='*unknown*:')
