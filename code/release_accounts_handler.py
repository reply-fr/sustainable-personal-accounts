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

from logger import setup_logging, trap_exception
setup_logging()

from account import Account, State
from settings import Settings


@trap_exception
def handle_event(event, context, session=None):
    logging.info("Releasing managed accounts")
    processed = handle_managed_accounts(session=session)
    handle_managed_organizational_units(skip=processed, session=session)
    return '[OK]'


def handle_managed_accounts(session=None):
    logging.info("Processing configured accounts")
    ids = [id for id in Settings.enumerate_accounts(environment=os.environ['ENVIRONMENT_IDENTIFIER'], session=session)]
    for id in ids:
        handle_account(account=id, session=session)
    logging.info("All configured accounts have been processed")
    return ids


def handle_managed_organizational_units(skip=[], session=None):
    logging.info("Processing configured organizational units")
    for identifier in Settings.enumerate_organizational_units(environment=os.environ['ENVIRONMENT_IDENTIFIER'], session=session):
        logging.info(f"Scanning organizational unit '{identifier}'")
        for account in Account.list(parent=identifier, skip=skip, session=session):
            handle_account(account=account, session=session)
    logging.info("All configured organizational units have been processed")


def handle_account(account, session=None):
    item = Account.describe(account, session=session)
    state = item.tags.get('account:state')
    if not item.is_active:
        logging.info(f"Ignoring inactive account '{account}'")
    elif state and state == State.RELEASED.value:
        logging.info(f"Ignoring account '{account}' that is in state '{state}'")
    else:
        Account.move(account=account, state=State.RELEASED, session=session)
