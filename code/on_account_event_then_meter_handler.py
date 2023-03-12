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

from boto3.session import Session
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


@trap_exception
def handle_account_event(event, context=None, emit=None):
    input = Events.decode_account_event(event)
    transactions = KeyValueStore(table_name=os.environ.get('METERING_TRANSACTIONS_DATASTORE', 'SpaTransactionsTable'),
                                 ttl=os.environ.get('METERING_TRANSACTIONS_TTL', str(30 * 60)))

    if input.label == 'CreatedAccount':
        handle_created_event(input.account, transactions=transactions)

    elif input.label == 'ExpiredAccount':
        handle_expired_event(input.account, transactions=transactions)

    elif input.label == 'ReleasedAccount':
        handle_released_event(input.account, transactions=transactions, emit=emit)

    else:
        logging.debug(f"Do not meter event '{input.label}'")

    return f"[OK] {input.label} {input.account}"


def handle_created_event(account_id, transactions):
    hash = f"OnBoarding {account_id}"
    logging.info(f"Beginning transaction '{hash}'")
    transaction = {'transaction': 'on-boarding',
                   'account': account_id,
                   'begin': time(),
                   'identifier': str(uuid4())}
    logging.debug(transaction)
    transactions.remember(hash, value=transaction)


def handle_expired_event(account_id, transactions):
    hash = f"Maintenance {account_id}"
    logging.info(f"Beginning transaction '{hash}'")
    transaction = {'transaction': 'maintenance',
                   'account': account_id,
                   'begin': time(),
                   'identifier': str(uuid4())}
    logging.debug(transaction)
    transactions.remember(hash, value=transaction)


def handle_released_event(account_id, transactions, emit=None):
    update_maintenance_transaction(account_id, transactions=transactions, emit=emit)
    update_onboarding_transaction(account_id, transactions=transactions, emit=emit)


def update_maintenance_transaction(account_id, transactions, emit=None):
    hash = f"Maintenance {account_id}"
    ongoing = transactions.retrieve(hash)
    if ongoing:
        logging.info(f"Ending transaction '{hash}'")
        transactions.forget(hash)
        transaction = Account.list_tags(account_id)
        transaction['cost-center'] = get_cost_center(transaction)
        transaction.update(ongoing)
        transaction['end'] = time()
        transaction['duration'] = transaction['end'] - transaction['begin']
        logging.debug(transaction)
        emit = emit or Events.emit_spa_event
        emit(label='SuccessfulMaintenanceEvent',
             payload=transaction)
        put_metric_data(name='TransactionByCostCenter',
                        dimensions=[dict(Name='CostCenter', Value=transaction['cost-center']),
                                    dict(Name='Environment', Value=Events.get_environment())])
        put_metric_data(name='TransactionByLabel',
                        dimensions=[dict(Name='Label', Value="MaintenanceTransaction"),
                                    dict(Name='Environment', Value=Events.get_environment())])
    else:
        logging.error(f"Missing transaction '{hash}'")


def update_onboarding_transaction(account_id, transactions, emit=None):
    hash = f"OnBoarding {account_id}"
    ongoing = transactions.retrieve(hash)
    if ongoing:
        logging.info(f"Ending transaction '{hash}'")
        transactions.forget(hash)
        transaction = Account.list_tags(account_id)
        transaction['cost-center'] = get_cost_center(transaction)
        transaction.update(ongoing)
        transaction['end'] = time()
        transaction['duration'] = transaction['end'] - transaction['begin']
        logging.debug(transaction)
        emit = emit or Events.emit_spa_event
        emit(label='SuccessfulOnBoardingEvent',
             payload=transaction)
        put_metric_data(name='TransactionByCostCenter',
                        dimensions=[dict(Name='CostCenter', Value=transaction['cost-center']),
                                    dict(Name='Environment', Value=Events.get_environment())])
        put_metric_data(name='TransactionByLabel',
                        dimensions=[dict(Name='Label', Value="OnBoardingTransaction"),
                                    dict(Name='Environment', Value=Events.get_environment())])
    else:
        logging.error(f"Missing transaction '{hash}'")


def get_cost_center(transaction):
    return transaction.get("cost-center", "SharedServices")


def put_metric_data(name, dimensions, session=None):
    logging.debug(f"Putting data for metric '{name}' and dimensions '{dimensions}'...")
    session = session or Session()
    session.client('cloudwatch').put_metric_data(MetricData=[dict(MetricName=name,
                                                                  Dimensions=dimensions,
                                                                  Unit='Count',
                                                                  Value=1)],
                                                 Namespace="SustainablePersonalAccount")
    logging.debug("Done")


@trap_exception
def handle_stream_event(event, context=None, emit=None):

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

        handle_stream_record(record=payload, emit=emit)

    return "[OK]"


def handle_stream_record(record, emit=None):

    event_labels = {
        'on-boarding': 'FailedOnBoardingException',
        'maintenance': 'FailedMaintenanceException',
    }
    label = event_labels.get(record['transaction'], 'GenericException')

    emit = emit or Events.emit_spa_event
    emit(label=label, payload=record)
