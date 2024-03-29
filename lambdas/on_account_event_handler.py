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
from metric import put_metric_data
from settings import Settings


@trap_exception
def handle_account_event(event, context=None, emit=None):
    input = Events.decode_account_event(event)
    update_shadow_on_account_event(input)
    put_metrics(input)
    return f"[OK] {input.label} {input.account}"


def update_shadow_on_account_event(input):
    logging.info(f"Remembering '{input.label}' for '{input.account}'")
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


def put_metrics(input):
    if input.__dict__.get('message', None):
        logging.info(f"Logging '{input.label}' '{input.account}'\n{input.message}")

    put_metric_data(name='AccountEventsByAccount',
                    dimensions=[dict(Name='Account', Value=input.account),
                                dict(Name='Environment', Value=Events.get_environment())])
    put_metric_data(name='AccountEventsByLabel',
                    dimensions=[dict(Name='Label', Value=input.label),
                                dict(Name='Environment', Value=Events.get_environment())])


@trap_exception
def handle_console_login_event(event=None, context=None):
    logging.debug(event)
    if event["detail"]["responseElements"] != dict(ConsoleLogin="Success"):
        raise ValueError("This event is not a successful console login")
    account_id = event["detail"]["userIdentity"]["accountId"]
    identity_type = event["detail"]["userIdentity"]["type"]
    if identity_type == 'AssumedRole':
        identity = event["detail"]["userIdentity"]["arn"].split('/')[-1]
        handle_console_login_with_assumed_role(account_id=account_id, identity=identity)
    elif identity_type == 'IAMUser':
        user_name = event["detail"]["userIdentity"]["userName"]
        handle_console_login_with_account_user(account_id=account_id, user_name=user_name)
    elif identity_type == 'Root':
        handle_console_login_with_account_root(account_id=account_id)
    else:
        raise ValueError(f"Do not know how to handle identity type '{identity_type}'")
    return f"[OK] {account_id}"


def handle_console_login_with_assumed_role(account_id, identity):
    logging.info(f"Console login on account {account_id} with role assumed by {identity}")
    Settings.get_settings_for_account(identifier=account_id)  # exception if account is not managed
    update_shadow_on_console_login(account_id=account_id, identity=identity)
    put_activity_event(label='ConsoleLoginEvent', account_id=account_id)


def update_shadow_on_console_login(account_id, identity, shadows=None):
    shadows = shadows or get_table()
    shadow = shadows.retrieve(hash=str(account_id)) or {}
    stamps = shadow.get('stamps', {})
    stamps['ConsoleLogin'] = datetime.utcnow().replace(microsecond=0).isoformat()
    shadow['stamps'] = stamps
    shadow['identity_of_last_console_login'] = identity
    logging.debug(shadow)
    shadows.remember(hash=str(account_id), value=shadow)  # /!\ no lock


def put_activity_event(label, account_id, emit=None):
    payload = Account.list_tags(account_id)
    payload['cost-center'] = Account.get_cost_center(payload)
    payload.update(dict(transaction='console-login', account=account_id))
    emit = emit or Events.emit_activity_event
    emit(label=label, payload=payload)


def handle_console_login_with_account_user(account_id, user_name, emit=None):
    label = Account.get_account_label(account_id)
    logging.info(f"Console login on account {label} with IAM user {user_name} credentials")
    emit = emit or Events.emit_exception_event
    emit(label='ConsoleLoginWithIamUserException',
         payload=dict(account=account_id,
                      message=f"Check unexpected activity on account {label}",
                      title=f"Console login on account {label} with IAM user {user_name} credentials"))


def handle_console_login_with_account_root(account_id, emit=None):
    label = Account.get_account_label(account_id)
    logging.info(f"Console login on account {label} with account root credentials")
    emit = emit or Events.emit_exception_event
    emit(label='ConsoleLoginWithRootException',
         payload=dict(account=account_id,
                      message=f"Check unexpected activity on account {label}",
                      title=f"Console login on account {label} with account root credentials"))


@trap_exception
def handle_report(event=None, context=None):
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
    writer = DictWriter(buffer, fieldnames=['Cost Center', 'Cost Owner', 'Organizational Unit', 'Account', 'Name', 'Email', 'State', 'Console Login'])
    writer.writeheader()
    for record in records:
        item = record['value']
        try:
            ou_name = Account.get_organizational_unit_name(item['id'])
        except Exception as exception:
            logging.warning(exception)
            ou_name = "Unknown"
        row = {'Account': item['id'],
               'Cost Center': Account.get_cost_center(item['tags']),
               'Cost Owner': item['tags']['cost-owner'],
               'Email': item['email'],
               'Organizational Unit': ou_name,
               'Name': item['name'],
               'State': item['tags']['account-state'],
               'Console Login': item.get('stamps', {}).get('ConsoleLogin') or '-'}
        writer.writerow(row)
    return buffer.getvalue()


def get_report_path(today=None):
    today = today or date.today()
    return '/'.join([os.environ["REPORTING_INVENTORIES_PREFIX"],
                     f"{today.year:04d}",
                     f"{today.month:02d}",
                     f"{today.year:04d}-{today.month:02d}-{today.day:02d}-inventory.csv"])


def store_report(report):
    logging.info("Storing inventory report")
    logging.debug(report)
    boto3.client("s3").put_object(Bucket=os.environ['REPORTS_BUCKET_NAME'],
                                  Key=get_report_path(),
                                  Body=report)
