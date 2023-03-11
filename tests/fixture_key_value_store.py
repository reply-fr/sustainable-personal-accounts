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
from time import time


def create_my_table():
    boto3.client('dynamodb').create_table(TableName='my_table',
                                          KeySchema=[dict(AttributeName='Identifier', KeyType='HASH'),
                                                     dict(AttributeName='Order', KeyType='RANGE')],
                                          AttributeDefinitions=[dict(AttributeName='Identifier', AttributeType='S'),
                                                                dict(AttributeName='Order', AttributeType='S')],
                                          BillingMode='PAY_PER_REQUEST')
    boto3.client('dynamodb').get_waiter('table_exists').wait(TableName='my_table')


def populate_shadows_table():
    samples = [
        [('__account__', '222222222222'), ('__email__', 'alice@acme.com'), ('__name__', 'Alice'), ('__manager__', 'bob@acme.com'), ('__cost__', 'DevOps Tools'), ('__state__', 'released')],
        [('__account__', '333333333333'), ('__email__', 'bob@acme.com'), ('__name__', 'Bob'), ('__manager__', 'cesar@acme.com'), ('__cost__', 'Computing Tools'), ('__state__', 'released')],
        [('__account__', '444444444444'), ('__email__', 'cesar@acme.com'), ('__name__', 'César'), ('__manager__', 'alfred@acme.com'), ('__cost__', 'Tools'), ('__state__', 'released')],
        [('__account__', '555555555555'), ('__email__', 'efoe@acme.com'), ('__name__', 'Efoe'), ('__manager__', 'cesar@acme.com'), ('__cost__', 'Computing Tools'), ('__state__', 'released')],
        [('__account__', '666666666666'), ('__email__', 'francis@acme.com'), ('__name__', 'Francis'), ('__manager__', 'bob@acme.com'), ('__cost__', 'DevOps Tools'), ('__state__', 'assigned')],
        [('__account__', '777777777777'), ('__email__', 'gustav@acme.com'), ('__name__', 'Gustav'), ('__manager__', 'bob@acme.com'), ('__cost__', 'DevOps Tools'), ('__state__', 'released')],
        [('__account__', '888888888888'), ('__email__', 'irene@acme.com'), ('__name__', 'Irène'), ('__manager__', 'bob@acme.com'), ('__cost__', 'DevOps Tools'), ('__state__', 'released')],
        [('__account__', '999999999999'), ('__email__', 'joe@acme.com'), ('__name__', 'Joe'), ('__manager__', 'alfred@acme.com'), ('__cost__', 'Reporting Tools'), ('__state__', 'purged')],
    ]

    template = json.dumps({'hash': '__account__',
                           'range': '-',
                           'value': {'id': '__account__',
                                     'arn': 'arn:aws:organizations::111111111111:account/o-abcdefghij/__account__',
                                     'email': '__email__',
                                     'name': '__name__',
                                     'is_active': True,
                                     'tags': {'account-state': '__state__',
                                              'cost-owner': '__manager__',
                                              'account-manager': '__manager__',
                                              'account-holder': '__email__',
                                              'cost-center': '__cost__'},
                                     'unit': 'ou-1234-12345678',
                                     'last_state': 'ReleasedAccount',
                                     'stamps': {'ExpiredAccount': '2023-03-09T22:11:49',
                                                'PurgeReport': '2023-03-09T22:13:29',
                                                'PurgedAccount': '2023-03-09T22:13:39',
                                                'AssignedAccount': '2023-03-09T22:13:59',
                                                'PreparedAccount': '2023-03-09T22:15:14',
                                                'ReleasedAccount': '2023-03-09T22:15:24'},
                                     'last_purge_log': "purge log"}})

    for sample in samples:
        text = template
        for keyword, replacement in sample:
            text = text.replace(keyword, replacement)
        item = json.loads(text)

        boto3.client('dynamodb').put_item(TableName='my_table',
                                          Item={'Identifier': dict(S=item['hash']),
                                                'Order': dict(S=item['range']),
                                                'Value': dict(S=json.dumps(item['value'])),
                                                'Expiration': dict(N=str(int(time()) + 500))},
                                          ReturnValues='NONE')

    return len(samples)
