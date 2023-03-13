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

import boto3
import botocore
from csv import DictWriter
from datetime import date
import io
import logging
import os
from datetime import datetime

from logger import setup_logging, trap_exception
setup_logging()

from account import Account
from events import Events
from key_value_store import KeyValueStore


@trap_exception
def handle_account_event(event, context=None, emit=None):
    input = Events.decode_account_event(event)
    logging.info(f"Remembering {input.label} for {input.account}")
    shadows = get_table()
    shadow = shadows.retrieve(hash=str(input.account)) or {}
    try:
        shadow.update(Account.describe(input.account).__dict__)
    except botocore.exceptions.ClientError:
        logging.warning(f"No information could be found for account {input.account}")
    if input.label == 'PreparationReport':
        shadow['last_preparation_log'] = input.message or "no log"
    elif input.label == 'PurgeReport':
        shadow['last_purge_log'] = input.message or "no log"
    else:
        shadow['last_state'] = input.label
    stamps = shadow.get('stamps', {})
    stamps[input.label] = datetime.utcnow().replace(microsecond=0).isoformat()
    shadow['stamps'] = stamps
    logging.debug(shadow)
    shadows.remember(hash=str(input.account), value=shadow)  # /!\ no lock
    return f"[OK] {input.label} {input.account}"


@trap_exception
def handle_reporting(event=None, context=None):
    logging.info("Producing inventory reports from shadows")
    store = get_table()
    report = build_report(records=store.scan())  # /!\ memory-bound
    store_report(report)
    return "[OK]"


def get_table():
    return KeyValueStore(table_name=os.environ.get('METERING_SHADOWS_DATASTORE', 'SpaShadowsTable'),
                         ttl=os.environ.get('METERING_SHADOWS_TTL', str(181 * 24 * 60 * 60)))


def build_report(records):
    logging.info("Building inventory report from shadows")
    buffer = io.StringIO()
    writer = DictWriter(buffer, fieldnames=['cost_center', 'cost_owner', 'account', 'email', 'name', 'state'])
    writer.writeheader()
    for record in records:
        item = record['value']
        row = dict(account=item['id'],
                   cost_center=item['tags']['cost-center'],
                   cost_owner=item['tags']['cost-owner'],
                   email=item['email'],
                   name=item['name'],
                   state=item['tags']['account-state'])
        writer.writerow(row)
    return buffer.getvalue()


def store_report(report):
    logging.info("Storing inventory report")
    logging.debug(report)
    boto3.client("s3").put_object(Bucket=os.environ['REPORTS_BUCKET_NAME'],
                                  Key=get_report_key(),
                                  Body=report)


def get_report_key(today=None):
    today = today or date.today()
    return '/'.join([os.environ["REPORTING_INVENTORIES_PREFIX"],
                     f"{today.year:04d}",
                     f"{today.month:02d}",
                     f"{today.year:04d}-{today.month:02d}-{today.day:02d}-inventory.csv"])
