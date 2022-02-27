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
from types import SimpleNamespace

from boto3.session import Session


class Events:

    EVENT_LABELS = [
        'AssignedAccount',
        'CreatedAccount',
        'ExpiredAccount',
        'PreparedAccount',
        'PurgedAccount',
        'ReleasedAccount']

    @classmethod
    def emit(cls, label, account, session=None):
        event = cls.build_event(label=label, account=account)
        cls.put_event(event=event, session=session)
        return event

    @classmethod
    def build_event(cls, label, account):
        if label not in cls.EVENT_LABELS:
            raise ValueError(f"Invalid event label '{label}'")
        if len(account) != 12:
            raise ValueError(f"Invalid account identifier '{account}'")
        return dict(Detail=json.dumps(dict(Account=account,
                                           Environment=cls.get_environment())),
                    DetailType=label,
                    Source='SustainablePersonalAccounts')

    @classmethod
    def get_environment(cls):
        return os.environ.get('ENVIRONMENT_IDENTIFIER', 'Spa')

    @classmethod
    def put_event(cls, event, session=None):
        logging.info(f"Putting event {event}")
        if os.environ.get("DRY_RUN") == "FALSE":
            session = session or Session()
            session.client('events').put_events(Entries=[event])
            logging.info("Done")
        else:
            logging.warning("Dry-run mode - no event has been put")

    @staticmethod
    def decode_codebuild_event(event, match=None):
        decoded = SimpleNamespace()

        decoded.account = event['account']
        if len(decoded.account) != 12:
            raise ValueError(f"Invalid account identifier '{decoded.account}'")

        decoded.project = event['detail']['project-name']
        if match and match != decoded.project:
            logging.debug(f"Expecting project name '{match}'")
            raise ValueError(f"Ignored project '{decoded.project}'")

        decoded.status = event['detail']['build-status']
        if decoded.status != 'SUCCEEDED':
            raise ValueError(f"Ignored status '{decoded.status}'")

        return decoded

    @classmethod
    def decode_local_event(cls, event, match=None):
        decoded = SimpleNamespace()

        decoded.environment = event['detail'].get('Environment', 'None')
        if decoded.environment != cls.get_environment():
            raise ValueError(f"Unexpected environment '{decoded.environment}'")

        decoded.account = event['detail'].get('Account', 'None')
        if len(decoded.account) != 12:
            raise ValueError(f"Invalid account identifier '{decoded.account}'")

        decoded.label = event['detail-type']
        if match and match != decoded.label:
            raise ValueError(f"Unexpected event label '{decoded.label}'")

        return decoded

    @staticmethod
    def decode_move_account_event(event, matches=None):
        decoded = SimpleNamespace()

        decoded.account = event['detail']['requestParameters']['accountId']
        if len(decoded.account) != 12:
            raise ValueError(f"Invalid account identifier '{decoded.account}'")

        decoded.organizational_unit = event['detail']['requestParameters']['destinationParentId']
        if matches and decoded.organizational_unit not in matches:
            raise ValueError(f"Unexpected event source '{decoded.organizational_unit}'")

        return decoded

    @staticmethod
    def decode_tag_account_event(event, match=None):
        decoded = SimpleNamespace()

        decoded.account = event['detail']['requestParameters']['resourceId']
        if len(decoded.account) != 12:
            raise ValueError(f"Invalid account identifier '{decoded.account}'")

        for item in event['detail']['requestParameters']['tags']:
            if item['key'] == 'account:state':
                decoded.state = item['value']
                if match and match.value != decoded.state:
                    raise ValueError(f"Unexpected state '{decoded.state}' for this function")
                return decoded
        raise ValueError("Missing tag 'account:state' in this event")

    @staticmethod
    def make_event(template, context):
        with open(template) as stream:
            text = stream.read()
            for key, value in context.items():
                text = text.replace('___' + key + '___', value)
            return json.loads(text)
