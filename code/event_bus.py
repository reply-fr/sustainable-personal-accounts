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

import boto3


class EventFactory:
    STATE_LABELS = [
        'AssignedAccount',
        'CreatedAccount',
        'ExpiredAccount',
        'PreparedAccount',
        'PurgedAccount',
        'ReleasedAccount']

    @classmethod
    def emit(cls, label, account, client=None):
        event = cls.build_event(label=label, account=account)
        cls.put_event(event=event, client=client)

    @classmethod
    def build_event(cls, label, account):
        if label not in cls.STATE_LABELS:
            raise AttributeError(f'Invalid state type {label}')
        return dict(Detail=json.dumps(dict(Account=account)),
                    DetailType=label,
                    Source='SustainablePersonalAccounts')

    @classmethod
    def put_event(cls, event, client=None):
        logging.info(f'put_event: {event}')
        if os.environ.get("DRY_RUN") == "true":
            return
        client = client if client else boto3.client('events')
        client.put_events(Entries=[event])

    @staticmethod
    def decode_local_event(event, match=None):
        decoded = SimpleNamespace()

        decoded.account = event['detail']['Account']
        if len(decoded.account) != 12:
            raise ValueError(f"Invalid account identifier '{decoded.account}'")

        decoded.state = event['detail-type']
        if match and match != decoded.state:
            raise ValueError(f"Unexpected state '{decoded.state}'")

        return decoded

    @staticmethod
    def decode_move_account_event(event, match=None):
        decoded = SimpleNamespace()

        decoded.account = event['detail']['requestParameters']['accountId']
        if len(decoded.account) != 12:
            raise ValueError(f"Invalid account identifier '{decoded.account}'")

        decoded.organizational_unit = event['detail']['requestParameters']['destinationParentId']
        if match and match != decoded.organizational_unit:
            raise ValueError(f"Unexpected event source '{decoded.organizational_unit}' for this function")

        return decoded

    @staticmethod
    def decode_tag_account_event(event, match=None):
        decoded = SimpleNamespace()

        decoded.account = event['requestParameters']['resourceId']
        if len(decoded.account) != 12:
            raise ValueError(f"Invalid account identifier '{decoded.account}'")

        for item in event['requestParameters']['tags']:
            if item['key'] == 'account:state':
                decoded.state = item['value']
                if match and match != decoded.state:
                    raise ValueError(f"Unexpected state '{decoded.state}' for this function")
                return decoded
        raise ValueError("Missing tag 'account:state' in this event")

        return decoded

    @staticmethod
    def make_event(template, context):
        with open(template) as stream:
            text = stream.read()
            for key, value in context.items():
                text = text.replace('___' + key + '___', value)
            return json.loads(text)
