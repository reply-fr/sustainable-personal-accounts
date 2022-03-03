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
def handle_event(event, context, session=None):
    logging.info("Checking personal accounts")
    units = get_organizational_units(session=session)
    for unit in units.keys():
        logging.info(f"Scanning organizational unit '{unit}'")
        logging.debug(units[unit])
        for account in Account.list(parent=unit, session=session):
            handle_account(account=account, unit=units[unit], session=session)
    logging.info("All configured organizational units have been scanned")
    return '[OK]'


def handle_account(account, unit=None, session=None):
    item = Account.describe(account, session=session)
    try:
        validate_tags(account=account, tags=item.tags)
        if unit:
            validate_unit_configuration(item, unit=unit)
    except ValueError as error:
        logging.error(error)


def validate_tags(account, tags):
    if 'account:holder' not in tags.keys():
        raise ValueError(f"Account '{account}' has no tag 'account:holder'")
    holder = tags['account:holder']
    if not Account.validate_holder(holder):
        raise ValueError(f"Account '{account}' assigned to '{holder}' has invalid value for tag 'account:holder'")
    if 'account:state' not in tags.keys():
        raise ValueError(f"Account '{account}' assigned to '{holder}' has no tag 'account:state'")
    state = tags['account:state']
    if not Account.validate_state(state):
        raise ValueError(f"Account '{account}' assigned to '{holder}' has invalid value '{state}' for tag 'account:state'")
    if state not in [State.RELEASED.value]:
        logging.warning(f"Account '{account}' assigned to '{holder}' is in transient state '{state}'")
    logging.info(f"Account '{account}' assigned to '{holder}' is valid")


def validate_unit_configuration(item, unit):
    expected_tags = unit.get("account_tags", {})
    for key in expected_tags.keys():
        if key not in item.tags.keys():
            logging.warning(f"Account '{item.id}' assigned to '{item.tags['account:holder']}' has no tag '{key}'")
        elif item.tags[key] != expected_tags[key]:
            logging.warning(f"Account '{item.id}' assigned to '{item.tags['account:holder']}' has unexpected value '{item.tags[key]}' for tag '{key}'")
