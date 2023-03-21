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
import pymsteams

from .logger import setup_logging, trap_exception
setup_logging()

from .events import Events


@trap_exception
def handle_spa_event(event, context, session=None):
    logging.debug(json.dumps(event))

    try:
        item = Events.decode_spa_event(event)
        post_message(message=item.payload, session=session)
    except Exception:
        message = dict(Subject="Message title", Message="Message body")
        post_message(message=message, session=session)

    return '[OK]'


def post_message(message, session=None):
    logging.debug("Relaying message")
    microsoft_webhook = os.environ.get('MICROSOFT_WEBHOOK_ON_ALERTS', None)
    if microsoft_webhook:
        logging.info(f"Publishing on Microsoft Webhook: {microsoft_webhook}")
        handler = pymsteams.connectorcard(microsoft_webhook)
        handler.title(message['Subject'])
        handler.text(message['Message'])
        handler.send()
