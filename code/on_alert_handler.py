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


MESSAGE_TEMPLATE = """
You will find below a copy of the alert that has been sent automatically to the holder of account '{account_id}':

----

{message}
"""


SUBJECT_TEMPLATE = "Alert on account '{account_id}'"


@trap_exception
def handle_queue_event(event, context, session=None):
    logging.info("Receiving records from queue")
    logging.debug(json.dumps(event))
    for record in event['Records']:
        handle_record(record, session=session)
    return '[OK]'


def handle_record(record, session=None):
    if record['eventSource'] == "aws:sqs":
        handle_sqs_record(record, session=session)
    else:
        raise AttributeError("Unable to handle source '{}'".format(record['eventSource']))


def handle_sqs_record(record, session=None):
    body = json.loads(record['body'])
    logging.debug(body)
    topic_arn = body['TopicArn']
    account_id = topic_arn.split(':')[4]

    notification = dict(TopicArn=os.environ['TOPIC_ARN'],
                        Message=get_message(account_id=account_id, message=body['Message']),
                        Subject=get_subject(account_id=account_id))
    logging.info(f"Publishing notification: {notification}")

    session = session or Session()
    session.client('sns').publish(**notification)


def get_message(account_id, message) -> str:
    return MESSAGE_TEMPLATE.format(account_id=account_id, message=message).strip()


def get_subject(account_id) -> str:
    return SUBJECT_TEMPLATE.format(account_id=account_id).strip()
