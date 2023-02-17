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

from boto3.session import Session

from logger import setup_logging, trap_exception
setup_logging()

from account import Account
from events import Events


CODEBUILD_TEMPLATE = """
You will find below details on failing CodeBuild project ran on account '{account}':

- account: {account}
- project: {project}
- status: {status}
"""


NOTIFICATION_TEMPLATE = """
You will find below a copy of the alert that has been sent automatically to the holder of account '{account}':

----

{message}
"""


SUBJECT_TEMPLATE = "Alert on account '{account}'"


@trap_exception
def handle_codebuild_event(event, context, session=None):
    logging.info("Receiving failures from CodeBuild")
    logging.debug(event)
    input = Events.decode_codebuild_event(event)
    label = get_account_label(account_id=input.account, session=session)
    notification = dict(Message=get_codebuild_message(account=label, project=input.project, status=input.status),
                        Subject=get_subject(account=label))
    publish_notification(notification=notification, session=session)
    return '[OK]'


@trap_exception
def handle_queue_event(event, context, session=None):
    logging.info("Receiving records from queue")
    logging.debug(event)
    for record in event['Records']:
        handle_record(record, session=session)
    return '[OK]'


def handle_record(record, session=None):
    if record['eventSource'] == "aws:sqs":
        handle_sqs_record(record, session=session)
    else:
        logging.info(record)
        raise AttributeError("Unable to handle source '{}'".format(record['eventSource']))


def handle_sqs_record(record, session=None):
    logging.debug("Processing one record")
    logging.debug(record)
    try:
        body = json.loads(record['body'])
        account_id = body['TopicArn'].split(':')[4]
        relay_notification(message=body['Message'], account_id=account_id, session=session)
    except json.decoder.JSONDecodeError:
        relay_message(message=record['body'], session=session)


def relay_notification(account_id, message, session=None):
    logging.debug("Relaying alert notification")
    label = get_account_label(account_id=account_id, session=session)
    notification = dict(Message=get_notification_message(account=label, message=message),
                        Subject=get_subject(account=label))
    publish_notification(notification=notification, session=session)


def relay_message(message, session=None):
    logging.debug("Relaying message")
    notification = dict(Message=message,
                        Subject="Alert message")
    publish_notification(notification=notification, session=session)


def publish_notification(notification, session=None):
    logging.info(f"Publishing notification: {notification}")
    session = session or Session()
    publish_notification_on_microsoft_teams(notification=notification, session=session)
    publish_notification_on_sns(notification=notification, session=session)


def publish_notification_on_microsoft_teams(notification, session=None):
    Events.emit_spa_event("MessageToMicrosoftTeams", payload=json.dumps(notification), session=session)


def publish_notification_on_sns(notification, session=None):
    topic_arn = os.environ.get('TOPIC_ARN', None)
    if topic_arn:
        logging.info(f"Publishing on SNS: {topic_arn}")
        session = session or Session()
        session.client('sns').publish(TopicArn=topic_arn, **notification)


def get_account_label(account_id, session=None) -> str:
    account = Account.describe(account_id, session=session)
    return f"{account.id} ({account.email})"


def get_codebuild_message(account, project, status) -> str:
    return CODEBUILD_TEMPLATE.format(account=account, project=project, status=status).strip()


def get_notification_message(account, message) -> str:
    return NOTIFICATION_TEMPLATE.format(account=account, message=message).strip()


def get_subject(account) -> str:
    return SUBJECT_TEMPLATE.format(account=account).strip()
