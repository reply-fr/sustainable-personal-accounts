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

import botocore
import logging

from logger import setup_logging, trap_exception
setup_logging()

from account import Account, State
from settings import Settings


@trap_exception
def handle_schedule_event(event=None, context=None):
    logging.info("Expiring managed accounts")
    for account in Settings.enumerate_all_managed_accounts():
        handle_account(account=account)
    return "[OK]"


def handle_account(account):
    logging.debug(f"Handling account '{account}'")
    try:
        item = Account.describe(account)
        state = item.tags.get(Account.get_tag_key('state'))
        if not item.is_active:
            logging.info(f"Ignoring inactive account '{account}'")
        elif state and state != State.RELEASED.value:
            logging.info(f"Ignoring account '{account}' that is in state '{state}'")
        else:
            Account.move(account=account, state=State.EXPIRED)
    except botocore.exceptions.ClientError:
        logging.error(f"Unable to handle account '{account}'. Does it exist?")
