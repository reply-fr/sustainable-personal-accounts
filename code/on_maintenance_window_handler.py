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

from logger import setup_logging, trap_exception
setup_logging()

from account import Account, State
from session import get_organizational_units


@trap_exception
def handle_schedule_event(event, context, session=None):
    logging.info("Expiring personal accounts")
    units = get_organizational_units(session=session)
    for unit in units.keys():
        logging.info(f"Scanning organizational unit '{unit}'")
        for account in Account.list(parent=unit, session=session):
            item = Account.describe(account, session=session)
            if not item.is_active:
                logging.info(f"Ignoring inactive account '{account}'")
                continue
            state = item.tags.get('account:state')
            if state != State.RELEASED.value:
                logging.info(f"Ignoring account '{account}' that is in state '{state}'")
                continue
            Account.move(account=account, state=State.EXPIRED, session=session)
    logging.info("All configured organizational units have been scanned")

    return '[OK]'
