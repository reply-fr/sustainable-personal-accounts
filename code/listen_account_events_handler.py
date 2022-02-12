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

from logger import setup_logging
setup_logging()

import boto3

from event_bus import EventFactory


def handler(event, context, client=None):
    logging.info(json.dumps(event))

    input = EventFactory.decode_local_event(event)

    client = client if client else boto3.client('cloudwatch')  # allow code injection
    dimensions = [dict(Name='Account', Value=input.account),
                  dict(Name='State', Value=input.state)]

    # if os.environ.get("DRY_RUN") != "true":
    #     client.put_metric_data(MetricData=[dict(Dimensions=dimensions,
    #                                        MetricName='State transition',
    #                                        Unit='Count',
    #                                        Value=1)],
    #                            Namespace="SustainablePersonalAccount")

    return f"{input.state} {input.account}"
