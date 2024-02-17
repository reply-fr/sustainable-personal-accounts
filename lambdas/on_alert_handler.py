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


SUBJECT_TEMPLATE = "Budget alert on account '{account}'"


@trap_exception
def handle_codebuild_event(event, context, session=None):
    logging.info("Receiving failures from CodeBuild")
    logging.info(event)
    input = Events.decode_codebuild_event(event)
    Events.emit_exception_event(label='FailedCodebuildException',
                                payload=dict(account=input.account,
                                             message=f"You should inspect Codebuild project '{input.project}' that has status '{input.status}'",
                                             title=f"Codebuild event for account {input.account}"),
                                session=session)
    return f"[OK] {input.account}"


@trap_exception
def handle_sqs_event(event, context, session=None):
    logging.info("Receiving budget alerts from queue")
    for record in event['Records']:
        handle_sqs_record(record, session=session)
    return '[OK]'


def handle_sqs_record(record, session=None):
    logging.debug(record)
    try:
        body = json.loads(record['body'])
        account_id = body['TopicArn'].split(':')[4]
        label = Account.get_account_label(account=account_id, session=session)
        Events.emit_exception_event(label='BudgetAlertException',
                                    payload=dict(account=account_id,
                                                 message=get_notification_message(account=label, message=body['Message']),
                                                 title=get_subject(account=label)),
                                    session=session)
    except json.decoder.JSONDecodeError:
        Events.emit_spa_event(label='GenericException',
                              payload=dict(message=record['body'],
                                           title="Exception received over SQS"),
                              session=session)


def get_codebuild_message(account, project, status) -> str:
    return CODEBUILD_TEMPLATE.format(account=account, project=project, status=status).strip()


def get_notification_message(account, message) -> str:
    return NOTIFICATION_TEMPLATE.format(account=account, message=message).strip()


def get_subject(account) -> str:
    return SUBJECT_TEMPLATE.format(account=account).strip()
