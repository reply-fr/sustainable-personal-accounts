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

from boto3.session import Session
import json
import logging
import os
from types import SimpleNamespace

from account import Account


class Events:

    ACTIVITY_EVENT_LABELS = [
        'SuccessfulMaintenanceEvent',
        'SuccessfulOnBoardingEvent']

    CHAT_EVENT_LABELS = [
        'MessageFromSlack',
        'MessageToMicrosoftTeams',
        'MessageToSlack',
        'PinFromSlack',
        'ReactionFromSlack',
        'UpdateToSlack',
        'UploadToSlack']

    EXCEPTION_EVENT_LABELS = [
        'GenericException',
        'BudgetAlertException',
        'FailedCodebuildException',
        'FailedMaintenanceException',
        'FailedOnBoardingException']

    SPA_EVENT_LABELS = ACTIVITY_EVENT_LABELS + CHAT_EVENT_LABELS + EXCEPTION_EVENT_LABELS

    ACCOUNT_EVENT_LABELS = [
        'AssignedAccount',
        'CreatedAccount',
        'ExpiredAccount',
        'PreparedAccount',
        'PurgedAccount',
        'ReleasedAccount',
        'PreparationReport',
        'PurgeReport']

    EVENT_LABELS = ACCOUNT_EVENT_LABELS + SPA_EVENT_LABELS

    DEFAULT_CONTENT_TYPE = 'application/json'

    @classmethod
    def build_account_event(cls, label, account, message=None):
        if label not in cls.ACCOUNT_EVENT_LABELS:
            raise ValueError(f"Invalid event label '{label}'")
        if len(account) != 12:
            raise ValueError(f"Invalid account identifier '{account}'")
        details = dict(Account=account,
                       Environment=cls.get_environment())
        if message:
            details['Message'] = message
        return dict(Detail=json.dumps(details),
                    DetailType=label,
                    Source='SustainablePersonalAccounts')

    @classmethod
    def build_spa_event(cls, label, payload=None, content_type=None):
        if label not in cls.SPA_EVENT_LABELS:
            raise ValueError(f"Invalid event label '{label}'")
        details = {
            'ContentType': content_type or cls.DEFAULT_CONTENT_TYPE,
            'Environment': cls.get_environment(),
            'Payload': payload}
        return dict(Detail=json.dumps(details),
                    DetailType=label,
                    Source='SustainablePersonalAccounts')

    @classmethod
    def decode_account_event(cls, event, match=None):
        decoded = SimpleNamespace()

        decoded.environment = event['detail'].get('Environment', None)
        if decoded.environment != cls.get_environment():
            raise ValueError(f"Unexpected environment '{decoded.environment}'")

        decoded.account = event['detail'].get('Account', None)
        if len(decoded.account) != 12:
            raise ValueError(f"Invalid account identifier '{decoded.account}'")

        decoded.label = event['detail-type']
        if match and match != decoded.label:
            raise ValueError(f"Unexpected event label '{decoded.label}'")

        decoded.message = event['detail'].get('Message', None)

        return decoded

    @staticmethod
    def decode_codebuild_event(event, match=None):
        decoded = SimpleNamespace()

        decoded.account = event['account']
        if len(decoded.account) != 12:
            raise ValueError(f"Invalid account identifier '{decoded.account}'")

        decoded.project = event['detail']['project-name']
        if match and match != decoded.project:
            logging.debug(f"Expecting project name '{match}'")
            raise ValueError(f"Ignoring project '{decoded.project}'")

        decoded.status = event['detail']['build-status']

        return decoded

    @staticmethod
    def decode_organization_event(event, matches=None):
        decoded = SimpleNamespace()

        decoded.account = event['detail']['requestParameters']['accountId']
        if len(decoded.account) != 12:
            raise ValueError(f"Invalid account identifier '{decoded.account}'")

        decoded.organizational_unit = event['detail']['requestParameters']['destinationParentId']
        if matches and decoded.organizational_unit not in matches:
            logging.debug(matches)
            raise ValueError(f"Unexpected event source '{decoded.organizational_unit}'")

        return decoded

    @classmethod
    def decode_spa_event(cls, event, match=None):
        decoded = SimpleNamespace()

        decoded.environment = event['detail'].get('Environment', None)
        if decoded.environment != cls.get_environment():
            raise ValueError(f"Unexpected environment '{decoded.environment}'")

        decoded.label = event['detail-type']
        if match and match != decoded.label:
            raise ValueError(f"Unexpected event label '{decoded.label}'")

        decoded.content_type = event['detail'].get('ContentType', cls.DEFAULT_CONTENT_TYPE)
        decoded.payload = event['detail'].get('Payload', None)

        return decoded

    @staticmethod
    def decode_tag_account_event(event, match=None):
        decoded = SimpleNamespace()

        decoded.account = event['detail']['requestParameters']['resourceId']
        if len(decoded.account) != 12:
            raise ValueError(f"Invalid account identifier '{decoded.account}'")

        expected = Account.get_tag_key('state')
        for item in event['detail']['requestParameters']['tags']:
            if item['key'] == expected:
                decoded.state = item['value']
                if match and match.value != decoded.state:
                    raise ValueError(f"Unexpected state '{decoded.state}' for this function")
                return decoded
        raise ValueError(f"Missing tag '{expected}' in this event")

    @classmethod
    def emit_account_event(cls, label, account, message=None, session=None):
        event = cls.build_account_event(label=label, account=account, message=message)
        cls.put_event(event=event, session=session)
        return event

    @classmethod
    def emit_spa_event(cls, label, payload=None, session=None):
        event = cls.build_spa_event(label=label, payload=payload)
        cls.put_event(event=event, session=session)
        return event

    @classmethod
    def get_environment(cls):
        return os.environ.get('ENVIRONMENT_IDENTIFIER', 'Spa')

    @classmethod
    def put_event(cls, event, session=None):
        logging.info(f"Putting event {event}")
        session = session or Session()
        session.client('events').put_events(Entries=[event])
        logging.debug("Done")

    @staticmethod
    def load_event_from_template(template, context):
        with open(template) as stream:
            text = stream.read()
            for key, value in context.items():
                text = text.replace('___' + key + '___', value)
            return json.loads(text)
