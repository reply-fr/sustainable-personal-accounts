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
import pytest
from time import time


@pytest.fixture
def given_an_empty_table():
    return _given_an_empty_table


def _given_an_empty_table():
    boto3.client('dynamodb').create_table(TableName='my_table',
                                          KeySchema=[dict(AttributeName='Identifier', KeyType='HASH'),
                                                     dict(AttributeName='Order', KeyType='RANGE')],
                                          AttributeDefinitions=[dict(AttributeName='Identifier', AttributeType='S'),
                                                                dict(AttributeName='Order', AttributeType='S')],
                                          BillingMode='PAY_PER_REQUEST')
    boto3.client('dynamodb').get_waiter('table_exists').wait(TableName='my_table')


@pytest.fixture
def given_a_table_of_activities():
    return _given_a_table_of_activities


def _given_a_table_of_activities():
    _given_an_empty_table()
    samples = [
        [('__transaction__', 'on-boarding'), ('__cost__', 'DevOps Tools'), ('__account__', '111111111111'), ('__stamp__', '22:08:29.749864')],
        [('__transaction__', 'maintenance'), ('__cost__', 'DevOps Tools'), ('__account__', '111111111111'), ('__stamp__', '22:13:12.049022')],
        [('__transaction__', 'on-boarding'), ('__cost__', 'DevOps Tools'), ('__account__', '222222222222'), ('__stamp__', '22:13:14.426446')],
        [('__transaction__', 'on-boarding'), ('__cost__', 'Computing Tools'), ('__account__', '333333333333'), ('__stamp__', '22:13:19.825640')],
        [('__transaction__', 'maintenance'), ('__cost__', 'DevOps Tools'), ('__account__', '222222222222'), ('__stamp__', '22:13:21.847512')],
        [('__transaction__', 'maintenance'), ('__cost__', 'Computing Tools'), ('__account__', '333333333333'), ('__stamp__', '22:13:26.828969')],
        [('__transaction__', 'on-boarding'), ('__cost__', 'DevOps Tools'), ('__account__', '666666666666'), ('__stamp__', '22:13:33.012642')],
        [('__transaction__', 'maintenance'), ('__cost__', 'Tools'), ('__account__', '444444444444'), ('__stamp__', '22:15:10.623627')],
        [('__transaction__', 'maintenance'), ('__cost__', 'Computing Tools'), ('__account__', '555555555555'), ('__stamp__', '22:15:13.266455')],
        [('__transaction__', 'maintenance'), ('__cost__', 'DevOps Tools'), ('__account__', '666666666666'), ('__stamp__', '22:15:16.646250')],
        [('__transaction__', 'on-boarding'), ('__cost__', 'DevOps Tools'), ('__account__', '888888888888'), ('__stamp__', '22:15:19.003777')],
        [('__transaction__', 'maintenance'), ('__cost__', 'DevOps Tools'), ('__account__', '777777777777'), ('__stamp__', '22:15:24.547341')],
        [('__transaction__', 'maintenance'), ('__cost__', 'DevOps Tools'), ('__account__', '888888888888'), ('__stamp__', '22:15:35.926257')],
        [('__transaction__', 'maintenance'), ('__cost__', 'Reporting Tools'), ('__account__', '999999999999'), ('__stamp__', '22:15:40.879809')],
        [('__transaction__', 'maintenance'), ('__cost__', 'DevOps Tools'), ('__account__', '111111111111'), ('__stamp__', '22:15:42.724794')],
        [('__transaction__', 'maintenance'), ('__cost__', 'Computing Tools'), ('__account__', '333333333333'), ('__stamp__', '22:15:49.867994')],
        [('__transaction__', 'maintenance'), ('__cost__', 'Computing Tools'), ('__account__', '555555555555'), ('__stamp__', '22:15:51.019361')],
        [('__transaction__', 'maintenance'), ('__cost__', 'DevOps Tools'), ('__account__', '777777777777'), ('__stamp__', '22:15:51.725803')],
        [('__transaction__', 'maintenance'), ('__cost__', 'Reporting Tools'), ('__account__', '999999999999'), ('__stamp__', '22:15:57.206767')],
        [('__transaction__', 'maintenance'), ('__cost__', 'DevOps Tools'), ('__account__', '222222222222'), ('__stamp__', '22:15:57.525895')],
        [('__transaction__', 'maintenance'), ('__cost__', 'Tools'), ('__account__', '444444444444'), ('__stamp__', '22:15:57.866044')],
        [('__transaction__', 'maintenance'), ('__cost__', 'DevOps Tools'), ('__account__', '666666666666'), ('__stamp__', '22:15:59.606731')],
        [('__transaction__', 'maintenance'), ('__cost__', 'DevOps Tools'), ('__account__', '888888888888'), ('__stamp__', '22:16:01.266087')],
        [('__transaction__', 'maintenance'), ('__cost__', 'DevOps Tools'), ('__account__', '111111111111'), ('__stamp__', '22:16:01.710460')],
        [('__transaction__', 'maintenance'), ('__cost__', 'DevOps Tools'), ('__account__', '222222222222'), ('__stamp__', '22:16:02.684601')],
        [('__transaction__', 'maintenance'), ('__cost__', 'Tools'), ('__account__', '444444444444'), ('__stamp__', '22:16:03.984360')],
        [('__transaction__', 'maintenance'), ('__cost__', 'Computing Tools'), ('__account__', '555555555555'), ('__stamp__', '22:16:07.390644')],
        [('__transaction__', 'maintenance'), ('__cost__', 'DevOps Tools'), ('__account__', '777777777777'), ('__stamp__', '22:16:07.895073')],
        [('__transaction__', 'maintenance'), ('__cost__', 'DevOps Tools'), ('__account__', '888888888888'), ('__stamp__', '22:16:13.005273')]
    ]

    template = json.dumps({'hash': '2023-03-09',
                           'range': '__stamp__',
                           'value': {"transaction": "__transaction__",
                                     "stamp": "2023-03-09T__stamp__",
                                     "cost-center": "__cost__",
                                     "account": "__account__",
                                     "begin": 1678627767.7734988,
                                     "identifier": "e740cfd8-918c-4aad-a7cf-9c633f5d3892",
                                     "end": 1678627885.2714968,
                                     "duration": 117.49799799919128}})

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


@pytest.fixture
def given_a_table_of_shadows():
    return _given_a_table_of_shadows


def _given_a_table_of_shadows():
    _given_an_empty_table()
    samples = [
        [('__account__', '222222222222'), ('__email__', 'alice@example.com'), ('__name__', 'Alice'), ('__manager__', 'bob@example.com'), ('__cost__', 'DevOps Tools'), ('__state__', 'released')],
        [('__account__', '333333333333'), ('__email__', 'bob@example.com'), ('__name__', 'Bob'), ('__manager__', 'cesar@example.com'), ('__cost__', 'Computing Tools'), ('__state__', 'released')],
        [('__account__', '444444444444'), ('__email__', 'cesar@example.com'), ('__name__', 'César'), ('__manager__', 'alfred@example.com'), ('__cost__', 'Tools'), ('__state__', 'released')],
        [('__account__', '555555555555'), ('__email__', 'efoe@example.com'), ('__name__', 'Efoe'), ('__manager__', 'cesar@example.com'), ('__cost__', 'Computing Tools'), ('__state__', 'released')],
        [('__account__', '666666666666'), ('__email__', 'francis@example.com'), ('__name__', 'Francis'), ('__manager__', 'bob@example.com'), ('__cost__', 'DevOps Tools'), ('__state__', 'assigned')],
        [('__account__', '777777777777'), ('__email__', 'gustav@example.com'), ('__name__', 'Gustav'), ('__manager__', 'bob@example.com'), ('__cost__', 'DevOps Tools'), ('__state__', 'released')],
        [('__account__', '888888888888'), ('__email__', 'irene@example.com'), ('__name__', 'Irène'), ('__manager__', 'bob@example.com'), ('__cost__', 'DevOps Tools'), ('__state__', 'released')],
        [('__account__', '999999999999'), ('__email__', 'joe@example.com'), ('__name__', 'Joe'), ('__manager__', 'alfred@example.com'), ('__cost__', 'Reporting Tools'), ('__state__', 'purged')],
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
                                     'stamps': {'AssignedAccount': '2023-03-09T22:13:59',
                                                'ConsoleLogin': '2023-03-09T22:13:29',
                                                'ExpiredAccount': '2023-03-09T22:11:49',
                                                'PreparedAccount': '2023-03-09T22:15:14',
                                                'PurgedAccount': '2023-03-09T22:13:39',
                                                'PurgeReport': '2023-03-09T22:13:29',
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
