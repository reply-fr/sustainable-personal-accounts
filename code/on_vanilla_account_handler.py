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

from logger import setup_logging, trap_exception
setup_logging()

from account import Account, State
from events import Events
from settings import Settings


@trap_exception
def handle_account_event(event, context, session=None):
    logging.debug(json.dumps(event))
    input = Events.decode_account_event(event=event)
    return handle_account(input.account, session=session)


@trap_exception
def handle_tag_event(event, context, session=None):
    logging.debug(json.dumps(event))
    input = Events.decode_tag_account_event(event=event, match=State.VANILLA)
    return handle_account(input.account, session=session)


def handle_account(account, session=None):
    settings = Settings.get_settings_for_account(environment=toggles.environment_identifier, identifier=account, session=session)
    item = Account.describe(account, session=session)
    updated = inspect_tags(item=item, settings=settings)
    if item.tags != updated:
        Account.tag(account, updated, session=session)
    return Events.emit('CreatedAccount', account)


def inspect_tags(item, settings):
    updated = item.tags.copy()

    updated.update(settings.get("account_tags", {}))

    updated['account:state'] = State.ASSIGNED.value

    holder = item.tags.get('account:holder') or item.email
    if not Account.validate_holder(holder):
        raise ValueError(f"Account '{item.id}' has invalid holder '{holder}'")
    updated['account:holder'] = holder

    return updated
