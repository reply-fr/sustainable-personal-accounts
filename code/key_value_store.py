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
from time import time


class KeyValueStore:

    def __init__(self, table_name, ttl=0):
        logging.debug(f"Using key-value store on DynamoDB table '{table_name}'")
        self.handler = boto3.client('dynamodb')
        self.table_name = table_name
        self.ttl = ttl or (366 * 24 * 60 * 60)  # default is one year TTL

    def forget(self, key, order='-'):
        logging.debug(f'Deleting record {key} from key-value store')
        self.handler.delete_item(TableName=self.table_name,
                                 Key={'Identifier': dict(S=key), 'Order': dict(S=order)},
                                 ReturnConsumedCapacity='NONE',
                                 ReturnValues='NONE')

    def remember(self, key, value, order='-'):
        logging.debug(f'Remembering record {key} in key-value store')
        self.handler.put_item(TableName=self.table_name,
                              Item={'Identifier': dict(S=key),
                                    'Order': dict(S=order),
                                    'Value': dict(S=json.dumps(value)),
                                    'Expiration': dict(N=str(int(time()) + int(self.ttl)))},
                              ReturnValues='NONE')

    def retrieve(self, key, order='-'):
        logging.debug(f'Retrieving record {key} from key-value store')
        result = self.handler.get_item(TableName=self.table_name,
                                       Key={'Identifier': dict(S=key), 'Order': dict(S=order)},
                                       ReturnConsumedCapacity='NONE')
        if 'Item' in result:
            return json.loads(result['Item']['Value']['S'])
