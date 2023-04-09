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
import logging
import os


class Email:

    @classmethod
    def send(cls, recipients, subject, text, session=None):
        logging.info("Sending an email")
        session = session or Session()
        ses = session.client('ses')
        try:
            ses.send_email(
                Source=os.environ['ORIGIN_EMAIL_RECIPIENT'],
                Destination=dict(ToAddresses=recipients),
                Message=dict(Subject=dict(Data=subject, Charset='UTF-8'),
                             Body=dict(Text=dict(Data=text, Charset='UTF-8')))
            )
            return '[OK]'
        except ses.exceptions.MessageRejected as exception:
            logging.exception(exception)
