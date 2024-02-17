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

from base64 import b64decode
import boto3
import botocore
from unittest.mock import ANY, Mock
from moto import mock_aws
import pytest

from lambdas import Email

# pytestmark = pytest.mark.wip


@pytest.mark.unit_tests
def test_get_mime_attachment():
    item = Email.get_mime_attachment(name='hello.txt', content=b'hello world!')
    assert item.is_multipart() is False
    assert set(item.keys()) == {'Content-Disposition', 'Content-Transfer-Encoding', 'Content-Type', 'MIME-Version'}
    assert item.get('Content-Disposition') == 'attachment; filename="hello.txt"'
    assert b64decode(item.get_payload()) == b'hello world!'

    item = Email.get_mime_attachment(name='héllo wôrld.txt', content=b'hello world!')
    assert item.is_multipart() is False
    assert set(item.keys()) == {'Content-Disposition', 'Content-Transfer-Encoding', 'Content-Type', 'MIME-Version'}
    assert item.get('Content-Disposition') == "attachment; filename*=utf-8''h%C3%A9llo%20w%C3%B4rld.txt"
    assert b64decode(item.get_payload()) == b'hello world!'


@pytest.mark.unit_tests
def test_get_mime_container():
    item = Email.get_mime_container(subject='subject', sender='alice@example.com', recipients='"Bob" <bob@example.com>, charles@example.com')
    assert item.is_multipart() is True
    assert set(item.keys()) == {'Content-Type', 'From', 'MIME-Version', 'Subject', 'To'}
    assert item.get('From') == 'alice@example.com'
    assert item.get('To') == '"Bob" <bob@example.com>, charles@example.com'
    assert item.get_payload() == []

    item = Email.get_mime_container(subject='subject', sender='zoe@example.com', recipients=['"Bob" <bob@example.com>', 'charles@example.com'])
    assert item.is_multipart() is True
    assert set(item.keys()) == {'Content-Type', 'From', 'MIME-Version', 'Subject', 'To'}
    assert item.get('From') == 'zoe@example.com'
    assert item.get('To') == '"Bob" <bob@example.com>, charles@example.com'
    assert item.get_payload() == []


@pytest.mark.unit_tests
def test_get_mime_message():
    item = Email.get_mime_message(text='hello world!')
    assert item.is_multipart() is False
    assert set(item.keys()) == {'Content-Type', 'MIME-Version', 'Content-Transfer-Encoding'}
    assert b64decode(item.get_payload()) == b'hello world!'

    item = Email.get_mime_message(text='hello world!', html='<h1>hello world!</h1>')
    assert item.is_multipart() is True
    assert set(item.keys()) == {'Content-Type', 'MIME-Version'}
    assert len(item.get_payload()) == 2


@pytest.mark.integration_tests
@mock_aws
def test_get_object_as_mime_attachment():

    s3 = boto3.client("s3")
    s3.create_bucket(Bucket="my_bucket",
                     CreateBucketConfiguration=dict(LocationConstraint='eu-west-3'))

    with pytest.raises(botocore.exceptions.ClientError):  # object does not exist
        Email.get_object_as_mime_attachment(object='s3://my_bucket/some/path/hello.txt')

    s3.put_object(Bucket="my_bucket",
                  Key='some/path/hello.txt',
                  Body='hello world!')

    item = Email.get_object_as_mime_attachment(object='s3://my_bucket/some/path/hello.txt')
    assert item.is_multipart() is False
    assert set(item.keys()) == {'Content-Disposition', 'Content-Transfer-Encoding', 'Content-Type', 'MIME-Version'}
    assert b64decode(item.get_payload()) == b'hello world!'

    with pytest.raises(ValueError):  # malformed object name
        Email.get_object_as_mime_attachment(object='my_bucket/some/path/hello.txt')


@pytest.mark.integration_tests
@mock_aws
def test_send_objects():

    s3 = boto3.client("s3")
    s3.create_bucket(Bucket="my_bucket",
                     CreateBucketConfiguration=dict(LocationConstraint='eu-west-3'))

    s3.put_object(Bucket="my_bucket",
                  Key='some/path/hello.txt',
                  Body='hello world!')

    parameters = dict(sender='alice@example.com',
                      recipients='bob@example.com, charles@example.com',
                      subject='monthly reports are available',
                      text='please find attached the reports for previous month',
                      html='<h1>Monthly reports</h1>\nPlease find attached the reports for previous month',
                      objects=['s3://my_bucket/some/path/hello.txt'])

    with pytest.raises(botocore.exceptions.ClientError):  # origin email has not been verified
        Email.send_objects(**parameters)

    ses = boto3.client('ses')
    ses.verify_email_identity(EmailAddress='alice@example.com')

    mock = Mock()
    assert Email.send_objects(**parameters, session=mock) == '[OK]'
    mock.client.return_value.send_raw_email.assert_called_with(
        Source='alice@example.com',
        Destinations=['bob@example.com', 'charles@example.com'],
        RawMessage={'Data': ANY}
    )

    parameters = dict(sender='alice@example.com',
                      recipients=['"Bob" <bob@example.com>', 'charles@example.com'],  # with a list instead of a string
                      subject='monthly reports are available',
                      text='please find attached the reports for previous month',
                      html='<h1>Monthly reports</h1>\nPlease find attached the reports for previous month',
                      objects=['s3://my_bucket/some/path/hello.txt'])
    assert Email.send_objects(**parameters) == '[OK]'

    mock = Mock()
    assert Email.send_objects(**parameters, session=mock) == '[OK]'
    mock.client.return_value.send_raw_email.assert_called_with(
        Source='alice@example.com',
        Destinations=['"Bob" <bob@example.com>', 'charles@example.com'],
        RawMessage={'Data': ANY}
    )


@pytest.mark.integration_tests
@mock_aws
def test_send_text():

    ses = boto3.client('ses')
    ses.verify_email_identity(EmailAddress='alice@example.com')

    parameters = dict(sender='alice@example.com',
                      subject='hello world!',
                      text="what's up, Doc?",
                      html='<h1>Hello world!</h1>')
    assert Email.send_text(recipients='bob@example.com, charles@example.com',
                           **parameters) == '[OK]'
    assert Email.send_text(recipients=['"Bob" <bob@example.com>', 'charles@example.com'],
                           **parameters) == '[OK]'

    mock = Mock()
    assert Email.send_text(recipients='bob@example.com, charles@example.com',
                           **parameters,
                           session=mock) == '[OK]'
    mock.client.return_value.send_raw_email.assert_called_with(
        Source='alice@example.com',
        Destinations=['bob@example.com', 'charles@example.com'],
        RawMessage={'Data': ANY}
    )

    mock = Mock()
    assert Email.send_text(recipients=['"Bob" <bob@example.com>', 'charles@example.com'],
                           **parameters,
                           session=mock) == '[OK]'
    mock.client.return_value.send_raw_email.assert_called_with(
        Source='alice@example.com',
        Destinations=['"Bob" <bob@example.com>', 'charles@example.com'],
        RawMessage={'Data': ANY}
    )
