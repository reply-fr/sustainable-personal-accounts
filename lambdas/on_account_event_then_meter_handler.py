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

import json
import logging
import os
from time import time
from uuid import uuid4

from logger import setup_logging, trap_exception
setup_logging()

from account import Account
from events import Events
from key_value_store import KeyValueStore
from metric import put_metric_data


@trap_exception
def handle_account_event(event, context=None, emit=None):
    input = Events.decode_account_event(event)
    transactions = KeyValueStore(table_name=os.environ.get('METERING_TRANSACTIONS_DATASTORE', 'SpaTransactionsTable'),
                                 ttl=os.environ.get('METERING_TRANSACTIONS_TTL', str(30 * 60)))

    if input.label == 'CreatedAccount':
        begin_transaction(transaction='on-boarding', account_id=input.account, transactions=transactions)

    elif input.label == 'ExpiredAccount':
        begin_transaction(transaction='maintenance', account_id=input.account, transactions=transactions)

    elif input.label == 'ReleasedAccount':
        end_transaction(input.account, transactions=transactions, emit=emit)

    else:
        logging.debug(f"Do not meter event '{input.label}'")

    return f"[OK] {input.label} {input.account}"


def begin_transaction(transaction, account_id, transactions):
    logging.info(f"Beginning transaction '{transaction}' for account '{account_id}")
    transaction = {'transaction': transaction,
                   'account': account_id,
                   'begin': time(),
                   'identifier': str(uuid4())}
    logging.debug(transaction)
    transactions.remember(account_id, value=transaction)


def end_transaction(account_id, transactions, emit=None):
    record = transactions.retrieve(account_id)
    if record:
        logging.info(f"Ending transaction '{hash}'")
        transactions.forget(account_id)
        transaction = Account.list_tags(account_id)
        transaction['cost-center'] = Account.get_cost_center(transaction)
        transaction.update(record)
        transaction['end'] = time()
        transaction['duration'] = transaction['end'] - transaction['begin']
        logging.debug(transaction)
        emit = emit or Events.emit_spa_event
        emit(label=get_event_label(record, success=True),
             payload=transaction)
        put_metric_data(name='TransactionsByCostCenter',
                        dimensions=[dict(Name='CostCenter', Value=Account.get_cost_center(transaction)),
                                    dict(Name='Environment', Value=Events.get_environment())])
        put_metric_data(name='TransactionsByLabel',
                        dimensions=[dict(Name='Label', Value=get_dimension_label(record)),
                                    dict(Name='Environment', Value=Events.get_environment())])
    else:
        logging.debug(f"No on-going transaction for account '{account_id}'")


@trap_exception
def handle_stream_event(event, context=None, emit=None):  # processing record expirations

    for item in event["Records"]:
        logging.debug(item)
        if item.get("eventName") != "REMOVE":
            continue
        if item.get("eventSource") != "aws:dynamodb":
            continue
        if item.get("userIdentity") != {"principalId": "dynamodb.amazonaws.com", "type": "Service"}:
            continue

        try:
            payload = json.loads(item["dynamodb"]["OldImage"]["Value"]["S"])
        except KeyError:
            logging.error(f"Unable to recognize expired transaction {item}")

        handle_expired_record(record=payload, emit=emit)

    return "[OK]"


def handle_expired_record(record, emit=None):
    logging.info(record)

    emit = emit or Events.emit_spa_event
    emit(label=get_event_label(record, success=False), payload=record)


def get_dimension_label(record):
    labels = {
        'on-boarding': 'OnBoardingTransaction',
        'maintenance': 'MaintenanceTransaction',
    }
    return labels[record['transaction']]


def get_event_label(record, success=True):
    labels = {
        'on-boarding': 'SuccessfulOnBoardingEvent' if success else 'FailedOnBoardingException',
        'maintenance': 'SuccessfulMaintenanceEvent' if success else 'FailedMaintenanceException',
    }
    return labels.get(record['transaction'], 'GenericException')

