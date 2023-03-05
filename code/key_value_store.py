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
import json
import logging
import os


class KeyValueStore:
    instances = {}

    @classmethod
    def get_instance(cls, path=None, cache=True):
        path = path or os.environ.get('KEY_VALUE_STORE_PATH', 'memory:')

        if path.startswith('dynamodb://'):
            if not cls.instances.get(path) or not cache:
                table_name = path[len('dynamodb://'):]
                cls.instances[path] = DynamoDbKeyValueStore(table_name=table_name)
            return cls.instances[path]

        elif path == 'memory:':
            if not cls.instances.get(path) or not cache:
                cls.instances[path] = MemoryKeyValueStore()
            return cls.instances[path]

        raise AttributeError(f"Unknown keystore path '{path}")


class DynamoDbKeyValueStore:

    def __init__(self, table_name):
        logging.debug(f"Using key-value store on DynamoDB table '{table_name}'")
        self.handler = boto3.client('dynamodb')
        self.table_name = table_name

    def forget(self, key):
        logging.debug(f'Deleting record {key} from key-value store')
        self.handler.delete_item(TableName=self.table_name,
                                 Key={'Identifier': dict(S=key)},
                                 ReturnConsumedCapacity='NONE',
                                 ReturnValues='NONE')

    def remember(self, key, value):
        logging.debug(f'Remembering record {key} in key-value store')
        self.handler.put_item(TableName=self.table_name,
                              Item={'Identifier': dict(S=key), 'Value': dict(S=json.dumps(value))},
                              ReturnValues='NONE')

    def retrieve(self, key):
        logging.debug(f'Retrieving record {key} from key-value store')
        result = self.handler.get_item(TableName=self.table_name,
                                       Key={'Identifier': dict(S=key)},
                                       ReturnConsumedCapacity='NONE')
        if 'Item' in result:
            return json.loads(result['Item']['Value']['S'])


class MemoryKeyValueStore:

    def __init__(self):
        logging.debug("Using key store in memory (useful only for local tests)")
        self.data = {}

    def forget(self, key):
        try:
            del self.data[key]
        except KeyError:
            pass

    def remember(self, key, value):
        self.data[key] = value

    def retrieve(self, key):
        return self.data.get(key)


datastore = KeyValueStore.get_instance()
