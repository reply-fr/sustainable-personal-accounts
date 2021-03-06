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
import os
import logging

from logger import setup_logging, trap_exception
setup_logging()

from botocore.exceptions import ClientError
from boto3.session import Session

from account import Account, State
from events import Events
from session import get_organizational_units_settings
from worker import Worker


@trap_exception
def handle_tag_event(event, context, session=None):
    logging.debug(json.dumps(event))
    input = Events.decode_tag_account_event(event=event, match=State.ASSIGNED)
    return handle_account(input.account, session=session)


def handle_account(account, session=None):
    all_settings = get_organizational_units_settings(session=session)
    details = Account.describe(account, session=session)
    if details.unit not in all_settings.keys():
        raise ValueError(f"Unexpected organizational unit '{details.unit}' for account '{account}'")
    result = Events.emit('AssignedAccount', account)
    settings = all_settings[details.unit]
    if 'preparation' not in settings.keys() or settings['preparation'].get('feature') != 'enabled':
        logging.info("Skipping the preparation of the account")
        Account.move(account=account, state=State.RELEASED, session=session)
    else:
        tag_account(account=account, settings=settings, session=session)
        prepare_account(details=details, settings=settings, session=session)
    return result


def tag_account(account, settings, session=None):
    if tags := settings.get("account_tags", {}):
        Account.tag(account, tags, session=session)


def prepare_account(details, settings, session=None):
    topic_arn = Worker.deploy_topic_for_alerts(account=details)
    subscribe_queue_to_topic(topic_arn=topic_arn, queue_arn=get_queue_arn(), session=session)
    Worker.prepare(account=details,
                   settings=settings,
                   event_bus_arn=os.environ['EVENT_BUS_ARN'],
                   topic_arn=topic_arn,
                   buildspec=get_buildspec(session=session),
                   session=session)


def get_buildspec(session=None):
    session = session or Session()
    item = session.client('ssm').get_parameter(Name=os.environ['PREPARATION_BUILDSPEC_PARAMETER'])
    return item['Parameter']['Value']


def get_queue_arn():
    return "arn:aws:sqs:{}:{}:{}Alerts".format(os.environ['AUTOMATION_REGION'],
                                               os.environ['AUTOMATION_ACCOUNT'],
                                               os.environ['ENVIRONMENT_IDENTIFIER'])


def subscribe_queue_to_topic(topic_arn, queue_arn, session=None):
    session = session or Session()
    sns = session.client('sns')
    try:
        logging.info(f"Subscribing central queue to topic '{topic_arn}'")
        sns.subscribe(TopicArn=topic_arn, Protocol='sqs', Endpoint=queue_arn)
    except ClientError as error:
        logging.error(error)
