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

from unittest.mock import patch
from moto import mock_organizations, mock_ssm
import os
import pytest

from lambdas import Settings

pytestmark = pytest.mark.wip
from tests.fixture_small_setup import given_a_small_setup


@pytest.mark.integration_tests
@mock_organizations
@mock_ssm
def test_enumerate_all_managed_accounts():
    context = given_a_small_setup()
    accounts = {i for i in Settings.enumerate_all_managed_accounts()}
    assert accounts == {context.crm_account, context.erp_account, context.alice_account, context.bob_account, '210987654321'}


@pytest.mark.integration_tests
@mock_organizations
@mock_ssm
def test_enumerate_accounts():
    context = given_a_small_setup()
    accounts = {i for i in Settings.enumerate_accounts()}
    assert accounts == {context.crm_account, context.erp_account, '210987654321'}


@pytest.mark.integration_tests
@mock_organizations
@mock_ssm
def test_enumerate_organizational_units():
    context = given_a_small_setup()
    accounts = {i for i in Settings.enumerate_organizational_units()}
    assert accounts == {context.sandbox_ou, 'ou-alien'}


@pytest.mark.unit_tests
@patch.dict(os.environ, dict(ENVIRONMENT_IDENTIFIER="yo"))
def test_get_account_parameter_name():
    name = Settings.get_account_parameter_name()
    assert name == '/yo/Accounts'

    name = Settings.get_account_parameter_name(identifier='1234')
    assert name == '/yo/Accounts/1234'


@pytest.mark.unit_tests
@patch.dict(os.environ, dict(ENVIRONMENT_IDENTIFIER="yo"))
def test_get_organizational_unit_parameter_name():
    name = Settings.get_organizational_unit_parameter_name()
    assert name == '/yo/OrganizationalUnits'

    name = Settings.get_organizational_unit_parameter_name(identifier='ou-abc')
    assert name == '/yo/OrganizationalUnits/ou-abc'


@pytest.mark.integration_tests
@mock_organizations
@mock_ssm
def test_get_account_settings():
    context = given_a_small_setup()
    settings = Settings.get_account_settings(identifier=context.crm_account)
    assert settings == context.settings_crm_account


@pytest.mark.integration_tests
@mock_organizations
@mock_ssm
def test_get_organizational_unit_settings():
    context = given_a_small_setup()
    settings = Settings.get_organizational_unit_settings(identifier=context.sandbox_ou)
    assert settings == context.settings_sandbox_ou


@pytest.mark.integration_tests
@mock_organizations
@mock_ssm
def test_get_settings_for_account():
    context = given_a_small_setup()
    settings = Settings.get_settings_for_account(identifier=context.alice_account)
    assert settings == context.settings_sandbox_ou


@pytest.mark.integration_tests
@patch.dict(os.environ, dict(ENVIRONMENT_IDENTIFIER="yo"))
@mock_organizations
@mock_ssm
def test_scan_settings_for_all_managed_accounts():
    given_a_small_setup(environment="yo")
    settings = Settings.scan_settings_for_all_managed_accounts()
    assert len(settings.keys()) == 4
