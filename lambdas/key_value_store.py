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
        self.dynamodb = boto3.client('dynamodb')
        self.table_name = table_name
        self.ttl = ttl or (366 * 24 * 60 * 60)  # default is one year TTL

    def forget(self, hash, range='-'):
        logging.debug(f"Deleting record {hash}/{range} from key-value store '{self.table_name}'")
        self.dynamodb.delete_item(TableName=self.table_name,
                                  Key={'Identifier': dict(S=hash), 'Order': dict(S=range)},
                                  ReturnConsumedCapacity='NONE',
                                  ReturnValues='NONE')

    def remember(self, hash, value, range='-'):
        logging.debug(f"Remembering record {hash}/{range} in key-value store '{self.table_name}'")
        self.dynamodb.put_item(TableName=self.table_name,
                               Item={'Identifier': dict(S=hash),
                                     'Order': dict(S=range),
                                     'Value': dict(S=json.dumps(value)),
                                     'Expiration': dict(N=str(int(time()) + int(self.ttl)))},
                               ReturnValues='NONE')

    def retrieve(self, hash, range='-'):
        logging.debug(f"Retrieving record {hash}/{range} from key-value store '{self.table_name}'")
        result = self.dynamodb.get_item(TableName=self.table_name,
                                        Key={'Identifier': dict(S=hash), 'Order': dict(S=range)},
                                        ReturnConsumedCapacity='NONE')
        if 'Item' in result:
            return json.loads(result['Item']['Value']['S'])

    def enumerate(self, hash):
        logging.debug(f"Enumerating records {hash} from key-value store '{self.table_name}'")
        parameters = dict(TableName=self.table_name,
                          KeyConditionExpression="Identifier = :hash",
                          ExpressionAttributeValues={':hash': dict(S=hash)},
                          ReturnConsumedCapacity='NONE')
        chunk = self.dynamodb.query(**parameters)
        while chunk.get('Items'):
            for item in chunk.get('Items'):
                yield dict(hash=item['Identifier']['S'],
                           range=item['Order']['S'],
                           value=json.loads(item['Value']['S']))
            more = chunk.get('LastEvaluatedKey')
            if more:
                chunk = self.dynamodb.query(ExclusiveStartKey=more, **parameters)
            else:
                break

    def scan(self):
        logging.debug(f"Scanning records from key-value store '{self.table_name}'")
        parameters = dict(TableName=self.table_name,
                          ReturnConsumedCapacity='NONE')
        chunk = self.dynamodb.scan(**parameters)
        while chunk.get('Items'):
            for item in chunk.get('Items'):
                yield dict(hash=item['Identifier']['S'],
                           range=item['Order']['S'],
                           value=json.loads(item['Value']['S']))
            more = chunk.get('LastEvaluatedKey')
            if more:
                chunk = self.dynamodb.scan(ExclusiveStartKey=more, **parameters)
            else:
                break
