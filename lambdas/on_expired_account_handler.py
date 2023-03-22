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

from logger import setup_logging, trap_exception
setup_logging()

from account import Account, State
from events import Events
from settings import Settings
from worker import Worker


@trap_exception
def handle_tag_event(event, context, session=None):
    logging.debug(json.dumps(event))
    input = Events.decode_tag_account_event(event=event, match=State.EXPIRED)
    return handle_account(input.account, session=session)


def handle_account(account, session=None):
    settings = Settings.get_settings_for_account(environment=os.environ['ENVIRONMENT_IDENTIFIER'], identifier=account, session=session)
    result = Events.emit_account_event('ExpiredAccount', account)
    if 'purge' not in settings.keys() or settings['purge'].get('feature') != 'enabled':
        logging.info("Skipping the purge of the account")
        Account.move(account=account, state=State.ASSIGNED, session=session)
    else:
        Worker.purge(account_id=account,
                     settings=settings,
                     event_bus_arn=os.environ['EVENT_BUS_ARN'],
                     buildspec=get_buildspec(session=session),
                     session=session)
    return result


def get_buildspec(session=None):
    session = session or Session()
    item = session.client('ssm').get_parameter(Name=os.environ['PURGE_BUILDSPEC_PARAMETER'])
    return item['Parameter']['Value']
