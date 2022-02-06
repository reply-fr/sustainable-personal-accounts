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

import os
import logging

from logger import setup_logging
setup_logging()

from event_bus import EventFactory


def handler(event, context):
    logging.debug(f'request: {event}')
    input = EventFactory.decode_aws_organizations_event(event)
    EventFactory.emit('CreatedAccount', input.account)
    print(f'we are handling account {input.account}')
    print(f'account has arrived on OU {input.organizational_unit}')
    if os.environ['VANILLA_ACCOUNTS_ORGANIZATIONAL_UNIT'] != input.organizational_unit:
        raise ValueError(f"We do not handle events for OU '{input.organizational_unit}'")
    # print("Source:" + event['source'])
    # print("Event Name:" + event['detail']['eventName'])
    # print("Account Id:" + event['detail']['requestParameters']['accountId'])
    # print("Destination OU Id:" + event['detail']['requestParameters']['destinationParentId'])
    # print("Source OU Id:" + event['detail']['requestParameters']['sourceParentId'])
    # print("Destination OU Id:" + event['detail']['requestParameters']['destinationParentId'] + "\n")

    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'text/plain'
        },
        'body': f'processing {input.account}'
    }
