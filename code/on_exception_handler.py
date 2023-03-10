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

import logging

from logger import setup_logging, trap_exception
setup_logging()

from boto3.session import Session

from events import Events


@trap_exception
def handle_exception(event, context, session=None):
    logging.debug(event)
    input = Events.decode_spa_event(event)

    put_metric_data(name='ExceptionsByLabel',
                    dimensions=[dict(Name='Label', Value=input.label),
                                dict(Name='Environment', Value=Events.get_environment())],
                    session=session)

    return f"[OK] {input.label}"


def put_metric_data(name, dimensions, session=None):
    logging.debug(f"Putting data for metric '{name}' and dimensions '{dimensions}'...")
    session = session or Session()
    session.client('cloudwatch').put_metric_data(MetricData=[dict(MetricName=name,
                                                                  Dimensions=dimensions,
                                                                  Unit='Count',
                                                                  Value=1)],
                                                 Namespace="SustainablePersonalAccount")
    logging.debug("Done")
