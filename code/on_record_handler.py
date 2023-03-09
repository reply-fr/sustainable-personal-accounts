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

from datetime import datetime
import logging
import os

from logger import setup_logging, trap_exception
setup_logging()

from events import Events
from key_value_store import KeyValueStore


@trap_exception
def handle_record(event, context=None, emit=None):
    input = Events.decode_spa_event(event)
    logging.info(f"Remembering {input.label}")
    logging.debug(input.__dict__)
    records = KeyValueStore(table_name=os.environ.get('METERING_RECORDS_DATASTORE', 'SpaMeteringTable'),
                            ttl=os.environ.get('METERING_RECORDS_TTL', str(366 * 24 * 60 * 60)))
    records.remember(key=datetime.utcnow().isoformat(), value=input.__dict__)
    return f"[OK] {input.label}"
