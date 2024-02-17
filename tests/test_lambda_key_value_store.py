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
from moto import mock_aws
import pytest

from lambdas import KeyValueStore

# pytestmark = pytest.mark.wip


@pytest.mark.unit_tests
@mock_aws
def test_key_value_store(given_an_empty_table):
    given_an_empty_table()

    store = KeyValueStore(table_name='my_table')
    store.remember(hash='a', value=dict(hello='world'))
    store.remember(hash='b', value=dict(life='is good'))
    assert store.retrieve(hash='a') == dict(hello='world')
    assert store.retrieve(hash='b') == dict(life='is good')

    store.remember(hash='a', value=dict(hello='universe'))
    assert store.retrieve(hash='a') == dict(hello='universe')
    assert store.retrieve(hash='b') == dict(life='is good')

    store.forget(hash='a')
    store.forget(hash='a')  # accept unknown key
    assert not store.retrieve(hash='a')
    assert store.retrieve(hash='b') == dict(life='is good')

    store.remember(hash='b', value=dict(life='is short'))
    assert not store.retrieve(hash='a')
    assert store.retrieve(hash='b') == dict(life='is short')

    store.remember(hash='a', value=dict(hello='world'))
    store.remember(hash='b', value=dict(life='is good'))
    result = boto3.client('dynamodb').scan(TableName='my_table',
                                           Select='ALL_ATTRIBUTES')
    assert len(result['Items']) == 2


@pytest.mark.unit_tests
@mock_aws
def test_enumerate(given_an_empty_table):
    given_an_empty_table()

    store = KeyValueStore(table_name='my_table')
    store.remember(hash='a', range='world', value=dict(hello='world'))
    store.remember(hash='a', range='universe', value=dict(hello='universe'))
    store.remember(hash='b', range='good', value=dict(life='is good'))
    store.remember(hash='b', range='short', value=dict(life='is short'))

    result = boto3.client('dynamodb').scan(TableName='my_table',
                                           Select='ALL_ATTRIBUTES')
    assert len(result['Items']) == 4

    assert list(store.enumerate(hash='a')) == [{'hash': 'a', 'range': 'universe', 'value': {'hello': 'universe'}},
                                               {'hash': 'a', 'range': 'world', 'value': {'hello': 'world'}}]
    assert list(store.enumerate(hash='b')) == [{'hash': 'b', 'range': 'good', 'value': {'life': 'is good'}},
                                               {'hash': 'b', 'range': 'short', 'value': {'life': 'is short'}}]


@pytest.mark.unit_tests
@mock_aws
def test_scan(given_an_empty_table):
    given_an_empty_table()

    store = KeyValueStore(table_name='my_table')
    store.remember(hash='a', range='world', value=dict(hello='world'))
    store.remember(hash='a', range='universe', value=dict(hello='universe'))
    store.remember(hash='b', range='good', value=dict(life='is good'))
    store.remember(hash='b', range='short', value=dict(life='is short'))

    assert list(store.scan()) == [{'hash': 'a', 'range': 'world', 'value': {'hello': 'world'}},
                                  {'hash': 'a', 'range': 'universe', 'value': {'hello': 'universe'}},
                                  {'hash': 'b', 'range': 'good', 'value': {'life': 'is good'}},
                                  {'hash': 'b', 'range': 'short', 'value': {'life': 'is short'}}]


@pytest.mark.unit_tests
@mock_aws
def test_scan_from_fixture(given_a_table_of_shadows):
    count = given_a_table_of_shadows()
    store = KeyValueStore(table_name='my_table')
    assert len(list(store.scan())) == count
