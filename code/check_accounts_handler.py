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
    logging.info("Checking managed accounts")
    processed = handle_managed_accounts(session=session)
    handle_managed_organizational_units(skip=processed, session=session)
    return '[OK]'


def handle_managed_accounts(session=None):
    logging.info("Scanning configured accounts")
    ids = [id for id in Settings.enumerate_accounts(environment=os.environ['ENVIRONMENT_IDENTIFIER'], session=session)]
    for identifier in ids:
        logging.info(f"Scanning account '{identifier}'")
        settings = Settings.get_account_settings(environment=os.environ['ENVIRONMENT_IDENTIFIER'],
                                                 identifier=identifier,
                                                 session=session)
        handle_account(account=identifier, settings=settings, session=session)
    logging.info("All configured accounts have been scanned")
    return ids


def handle_managed_organizational_units(skip=[], session=None):
    logging.info("Scanning configured organizational units")
    for identifier in Settings.enumerate_organizational_units(environment=os.environ['ENVIRONMENT_IDENTIFIER'], session=session):
        logging.info(f"Scanning organizational unit '{identifier}'")
        settings = Settings.get_organizational_unit_settings(environment=os.environ['ENVIRONMENT_IDENTIFIER'],
                                                             identifier=identifier,
                                                             session=session)
        for account in Account.list(parent=identifier, skip=skip, session=session):
            handle_account(account=account, settings=settings, session=session)
    logging.info("All configured organizational units have been scanned")


def handle_account(account, settings=None, session=None):
    item = Account.describe(account, session=session)
    try:
        validate_tags(item)
        if settings:
            validate_additional_tags(item, expected_tags=settings.get("account_tags", {}))
    except ValueError as error:
        logging.error(error)


def validate_tags(item):
    key = Account.get_tag_key('holder')
    if key not in item.tags.keys():
        raise ValueError(f"Account '{item.id}' has no tag '{key}'")
    holder = item.tags[key]
    if not Account.validate_holder(holder):
        raise ValueError(f"Account '{item.id}' assigned to '{holder}' has invalid value for tag '{key}'")


    key = Account.get_tag_key('state')
    if key not in item.tags.keys():
        raise ValueError(f"Account '{item.id}' assigned to '{holder}' has no tag '{key}'")
    state = item.tags[key]
    if not Account.validate_state(state):
        raise ValueError(f"Account '{item.id}' assigned to '{holder}' has invalid value '{state}' for tag '{key}'")
    if state not in [State.RELEASED.value]:
        logging.warning(f"Account '{item.id}' assigned to '{holder}' is in transient state '{state}'")
    logging.info(f"Account '{item.id}' assigned to '{holder}' is valid")


def validate_additional_tags(item, expected_tags):
    holder = item.tags.get(Account.get_tag_key('holder'))
    for key in expected_tags.keys():
        if key not in item.tags.keys():
            logging.warning(f"Account '{item.id}' assigned to '{holder}' has no tag '{key}'")
        elif item.tags[key] != expected_tags[key]:
            logging.warning(f"Account '{item.id}' assigned to '{holder}' has unexpected value '{item.tags[key]}' for tag '{key}'")
