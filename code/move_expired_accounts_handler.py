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

from logger import setup_logging
setup_logging()

from account import Account
from accounts import Accounts


def handler(event, context, client=None):
    logging.debug(json.dumps(event))

    for account in Accounts.list(parent=os.environ['RELEASED_ACCOUNTS_ORGANIZATIONAL_UNIT'], client=client):
        Account.move(account=account,
                     origin=os.environ['RELEASED_ACCOUNTS_ORGANIZATIONAL_UNIT'],
                     destination=os.environ['EXPIRED_ACCOUNTS_ORGANIZATIONAL_UNIT'],
                     client=client)
