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

import logging
import os
from time import time
from uuid import uuid4

from logger import setup_logging, trap_exception
setup_logging()

from events import Events
from key_value_store import KeyValueStore


@trap_exception
def handle_account_event(event, context=None, emit=None):
    input = Events.decode_account_event(event)
    transactions = KeyValueStore(table_name=os.environ.get('METERING_TRANSACTIONS_DATASTORE', 'SpaTransactionsTable'))

    if input.label == 'CreatedAccount':
        handle_created_event(input, transactions=transactions)

    elif input.label == 'ExpiredAccount':
        handle_expired_event(input, transactions=transactions)

    elif input.label == 'ReleasedAccount':
        handle_released_event(input, transactions=transactions, emit=emit)

    else:
        raise ValueError(f"Do not know how to handle event '{input.label}'")

    return f"[OK] {input.label} {input.account}"


def handle_created_event(input, transactions):
    key = f"OnBoarding {input.account}"
    logging.info(f"Beginning transaction '{key}'")
    transaction = {'account': input.account,
                   'begin': time(),
                   'identifier': str(uuid4())}
    transactions.remember(key, value=transaction)


def handle_expired_event(input, transactions):
    key = f"Maintenance {input.account}"
    logging.info(f"Beginning transaction '{key}'")
    transaction = {'account': input.account,
                   'begin': time(),
                   'identifier': str(uuid4())}
    transactions.remember(key, value=transaction)


def handle_released_event(input, transactions, emit=None):
    update_maintenance_transaction(input, transactions=transactions, emit=emit)
    update_onboarding_transaction(input, transactions=transactions, emit=emit)


def update_maintenance_transaction(input, transactions, emit=None):
    key = f"Maintenance {input.account}"
    transaction = transactions.retrieve(key)
    if transaction:
        logging.info(f"Ending transaction '{key}'")
        transactions.forget(key)
        transaction['end'] = time()
        transaction['duration'] = transaction['end'] - transaction['begin']
        logging.debug(transaction)
        emit = emit or Events.emit_spa_event
        emit(label='SuccessfulMaintenanceEvent',
             payload=transaction)


def update_onboarding_transaction(input, transactions, emit=None):
    key = f"OnBoarding {input.account}"
    transaction = transactions.retrieve(key)
    if transaction:
        logging.info(f"Ending transaction '{key}'")
        transactions.forget(key)
        transaction['end'] = time()
        transaction['duration'] = transaction['end'] - transaction['begin']
        logging.debug(transaction)
        emit = emit or Events.emit_spa_event
        emit(label='SuccessfulOnBoardingEvent',
             payload=transaction)
