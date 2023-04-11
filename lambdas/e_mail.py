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
from email import encoders
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
import logging
import os


class Email:

    @classmethod
    def get_mime_attachment(cls, name: str, content: str):
        logging.debug(f"Building MIME attachment for '{name}'")
        attachment = MIMEBase('application', 'octet-stream')
        attachment.set_payload(content)
        attachment.add_header('Content-Disposition', 'attachment', filename=name)
        encoders.encode_base64(attachment)
        return attachment

    @classmethod
    def get_mime_container(cls, subject: str, sender: str, recipients: str):
        container = MIMEMultipart('mixed')
        container['Subject'] = subject
        container['From'] = sender
        container['To'] = recipients if type(recipients) == str else ', '.join(recipients)
        return container

    @classmethod
    def get_mime_message(cls, text: str, html: str = None, charset: str = 'utf-8'):
        if not html:
            return MIMEText(text.encode(charset), 'plain', charset)
        message = MIMEMultipart('alternative')
        message.attach(MIMEText(text.encode(charset), 'plain', charset))
        message.attach(MIMEText(html.encode(charset), 'html', charset))
        return message

    @classmethod
    def get_object_as_mime_attachment(cls, object: str, session=None):
        if not object.startswith('s3://'):
            raise ValueError("Missing object prefix 's3://'")
        bucket, key = object[5:].split('/', 1)
        logging.debug(f"Looking for S3 bucket '{bucket}' and object '{key}'")
        session = session or Session()
        s3 = session.client('s3')
        stream = s3.get_object(Bucket=bucket, Key=key)['Body']
        return cls.get_mime_attachment(name=os.path.basename(key), content=stream.read())

    @classmethod
    def send_objects(cls, sender: str, recipients: str, subject: str, objects, text: str, html: str = None, session=None) -> str:
        logging.info("Sending an email with attachments from S3 objects")
        logging.debug(f"Subject: {subject}")
        container = cls.get_mime_container(subject=subject, sender=sender, recipients=recipients)
        container.attach(cls.get_mime_message(text=text, html=html))
        for object in objects:
            container.attach(cls.get_object_as_mime_attachment(object=object))
        return cls.send_raw_email(sender=sender, recipients=recipients, raw=container.as_string(), session=session)

    @classmethod
    def send_raw_email(cls, sender: str, recipients: str, raw: str, session=None) -> str:
        logging.debug("Sending SES raw message")
        session = session or Session()
        ses = session.client('ses')
        if type(recipients) == str:
            recipients = [recipient.strip() for recipient in recipients.split(',')]
        logging.debug(f"From: '{sender}'")
        logging.debug(f"To: '{recipients}'")
        ses.send_raw_email(Source=sender, Destinations=recipients, RawMessage=dict(Data=raw))
        return '[OK]'

    @classmethod
    def send_text(cls, sender: str, recipients: str, subject: str, text: str, html: str = None, session=None) -> str:
        logging.info("Sending an email with text")
        logging.debug(f"Subject: {subject}")
        container = cls.get_mime_container(subject=subject, sender=sender, recipients=recipients)
        container.attach(cls.get_mime_message(text=text, html=html))
        return cls.send_raw_email(sender=sender, recipients=recipients, raw=container.as_string(), session=session)
