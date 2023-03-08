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

from logger import setup_logging, trap_exception
setup_logging()

from events import Events
from key_value_store import KeyValueStore


@trap_exception
def handle_account_event(event, context=None, emit=None):
    input = Events.decode_account_event(event)
    logging.info(f"Remembering {input.label} for {input.account}")
    shadows = KeyValueStore(table_name=os.environ.get('METERING_SHADOWS_DATASTORE', 'SpaShadowsTable'))
    shadow = shadows.retrieve(key=str(input.account)) or {}
    if input.label == 'PreparationReport':
        shadow['last_preparation_log'] = input.message or "no log"
    elif input.label == 'PurgeReport':
        shadow['last_purge_log'] = input.message or "no log"
    else:
        shadow['last_state'] = input.label
    stamps = shadow.get('stamps', {})
    stamps[input.label] = time()
    shadow['stamps'] = stamps
    logging.debug(shadow)
    shadows.remember(key=str(input.account), value=shadow)
    return f"[OK] {input.label} {input.account}"
