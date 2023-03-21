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
logging.getLogger('botocore').setLevel(logging.CRITICAL)
logging.getLogger('urllib3').setLevel(logging.CRITICAL)

from boto3.session import Session
import json
from moto import mock_ssm
import pytest
from types import SimpleNamespace

from lambdas import Account, Settings

# pytestmark = pytest.mark.wip


def given_some_context(prefix='/Fake/'):

    session = Session(aws_access_key_id='testing',
                      aws_secret_access_key='testing',
                      aws_session_token='testing',
                      region_name='eu-west-1')

    context = SimpleNamespace(session=session)

    context.settings_123456789012 = {
        'account_tags': {'CostCenter': 'abc', 'Sponsor': 'Foo Bar'},
        'identifier': '123456789012',
        'note': 'a specific account',
        'preparation': {
            'feature': 'enabled',
            'variables': {'HELLO': 'WORLD'}
        },
        'purge': {
            'feature': 'disabled',
            'variables': {'DRY_RUN': 'TRUE'}
        }
    }
    session.client('ssm').put_parameter(Name=prefix + 'Accounts/123456789012',
                                        Value=json.dumps(context.settings_123456789012),
                                        Type='String')

    context.settings_567890123456 = {
        'account_tags': {'CostCenter': 'abc', 'Sponsor': 'Foo Bar'},
        'identifier': '567890123456',
        'note': 'another specific account',
        'preparation': {
            'feature': 'disabled',
            'variables': {'HELLO': 'MOON'}
        },
        'purge': {
            'feature': 'enabled',
            'variables': {'DRY_RUN': 'TRUE'}
        }
    }
    session.client('ssm').put_parameter(Name=prefix + 'Accounts/567890123456',
                                        Value=json.dumps(context.settings_567890123456),
                                        Type='String')

    context.settings_901234567890 = {
        'account_tags': {'CostCenter': 'abc', 'Sponsor': 'Foo Bar'},
        'identifier': '901234567890',
        'note': 'a third specific account',
        'preparation': {
            'feature': 'enabled',
            'variables': {'HELLO': 'JUPITER'}
        },
        'purge': {
            'feature': 'enabled',
            'variables': {'DRY_RUN': 'TRUE'}
        }
    }
    session.client('ssm').put_parameter(Name=prefix + 'Accounts/901234567890',
                                        Value=json.dumps(context.settings_901234567890),
                                        Type='String')

    context.settings_ou_1234 = {
        'account_tags': {'CostCenter': 'abc', 'Sponsor': 'Foo Bar'},
        'identifier': 'ou-1234',
        'note': 'a container for some accounts',
        'preparation': {
            'feature': 'enabled',
            'variables': {'HELLO': 'WORLD'}
        },
        'purge': {
            'feature': 'disabled',
            'variables': {'DRY_RUN': 'TRUE'}
        }
    }
    session.client('ssm').put_parameter(Name=prefix + 'OrganizationalUnits/ou-1234',
                                        Value=json.dumps(context.settings_ou_1234),
                                        Type='String')

    context.settings_ou_5678 = {
        'account_tags': {'CostCenter': 'abc', 'Sponsor': 'Foo Bar'},
        'identifier': 'ou-5678',
        'note': 'another container for some accounts',
        'preparation': {
            'feature': 'disabled',
            'variables': {'HELLO': 'MOON'}
        },
        'purge': {
            'feature': 'enabled',
            'variables': {'DRY_RUN': 'TRUE'}
        }
    }
    session.client('ssm').put_parameter(Name=prefix + 'OrganizationalUnits/ou-5678',
                                        Value=json.dumps(context.settings_ou_5678),
                                        Type='String')

    context.settings_ou_9012 = {
        'account_tags': {'CostCenter': 'abc', 'Sponsor': 'Foo Bar'},
        'identifier': 'ou-9012',
        'note': 'a third container for some accounts',
        'preparation': {
            'feature': 'enabled',
            'variables': {'HELLO': 'JUPITER'}
        },
        'purge': {
            'feature': 'enabled',
            'variables': {'DRY_RUN': 'TRUE'}
        }
    }
    session.client('ssm').put_parameter(Name=prefix + 'OrganizationalUnits/ou-9012',
                                        Value=json.dumps(context.settings_ou_9012),
                                        Type='String')

    return context


@pytest.mark.unit_tests
@mock_ssm
def test_enumerate_accounts():
    context = given_some_context(prefix='/Fake/')
    accounts = [i for i in Settings.enumerate_accounts(environment='Fake', session=context.session)]
    assert accounts == ['123456789012', '567890123456', '901234567890']


@pytest.mark.unit_tests
@mock_ssm
def test_enumerate_organizational_units():
    context = given_some_context(prefix='/Fake/')
    accounts = [i for i in Settings.enumerate_organizational_units(environment='Fake', session=context.session)]
    assert accounts == ['ou-1234', 'ou-5678', 'ou-9012']


@pytest.mark.unit_tests
def test_get_account_parameter_name():
    name = Settings.get_account_parameter_name(environment='yo')
    assert name == '/yo/Accounts'

    name = Settings.get_account_parameter_name(environment='yo', identifier='1234')
    assert name == '/yo/Accounts/1234'


@pytest.mark.unit_tests
def test_get_organizational_unit_parameter_name():
    name = Settings.get_organizational_unit_parameter_name(environment='yo')
    assert name == '/yo/OrganizationalUnits'

    name = Settings.get_organizational_unit_parameter_name(environment='yo', identifier='ou-abc')
    assert name == '/yo/OrganizationalUnits/ou-abc'


@pytest.mark.unit_tests
@mock_ssm
def test_get_account_settings():
    context = given_some_context(prefix='/Fake/')
    settings = Settings.get_account_settings(environment='Fake', identifier='567890123456', session=context.session)
    assert settings == context.settings_567890123456


@pytest.mark.unit_tests
@mock_ssm
def test_get_organizational_unit_settings():
    context = given_some_context(prefix='/Fake/')
    settings = Settings.get_organizational_unit_settings(environment='Fake', identifier='ou-5678', session=context.session)
    assert settings == context.settings_ou_5678


@pytest.mark.unit_tests
@mock_ssm
def test_get_settings_for_account(monkeypatch):
    context = given_some_context(prefix='/Fake/')

    def mock_describe(id, session):
        return SimpleNamespace(unit='ou-5678')

    monkeypatch.setattr(Account, 'describe', mock_describe)

    settings = Settings.get_settings_for_account(environment='Fake', identifier='98765432109', session=context.session)
    assert settings == context.settings_ou_5678
