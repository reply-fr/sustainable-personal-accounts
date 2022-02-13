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

import builtins
from io import BytesIO
from unittest.mock import patch
import os
import pytest
from types import SimpleNamespace

from resources import Configuration


pytestmark = pytest.mark.wip


@pytest.fixture
def toggles():
    builtins.toggles = SimpleNamespace()
    return builtins.toggles


def test_expand_text(toggles):
    text = 'this is some sample text with ___parameter___ to replace'
    toggles.parameter = '=value='
    test = Configuration.expand_text(text, toggles)
    assert test == 'this is some sample text with =value= to replace'


@pytest.mark.slow
@patch.dict(os.environ, dict(CDK_DEFAULT_ACCOUNT="123456789012", CDK_DEFAULT_REGION="eu-west-1"))
def test_initialize():

    Configuration.initialize(stream='tests/settings/sample_settings.yaml')
    assert builtins.toggles.dry_run is False
    assert builtins.toggles.aws_account is not None
    assert builtins.toggles.aws_environment is not None
    assert builtins.toggles.aws_region is not None

    with pytest.raises(FileNotFoundError):
        Configuration.initialize(stream='this*file*does*not*exist')


def test_set_default_values(toggles):
    Configuration.set_default_values()
    assert toggles.role_arn_to_put_events is None


def test_set_from_environment(toggles):
    environ = dict(
        ORGANIZATIONAL_UNITS="[\"ou-0987\"]",
        TRUSTED_PEER='4.3.2.1/32',
        NOT_MAPPED_VARIABLE="what'up Doc?",
        NONE_VARIABLE=None,
        NULL_VARIABLE='')

    Configuration.set_from_environment(environ=environ)
    assert toggles.__dict__.get('active_directory_domain_credentials') is None

    mapping = dict(
        organizational_units='ORGANIZATIONAL_UNITS'
    )
    Configuration.set_from_environment(environ=environ, mapping=mapping)
    assert toggles.organizational_units == ['ou-0987']


def test_set_from_settings(toggles):
    settings = dict(organizational_units=["foo bar"])
    Configuration.set_from_settings(settings)
    assert toggles.organizational_units == ["foo bar"]


@pytest.mark.slow
def test_set_from_yaml(toggles):
    Configuration.set_from_yaml('tests/settings/sample_settings.yaml')
    assert toggles.cockpit_markdown_text.strip() == '# Sustainable Personal Accounts Dashboard\nCurrently under active development (alpha)'
    assert toggles.dry_run is False
    assert toggles.expiration_expression == 'cron(0 18 ? * SAT *)'
    assert toggles.maximum_concurrent_executions == 50
    assert toggles.organizational_units == ['ou-1234']
    assert toggles.role_arn_to_manage_accounts == 'arn:aws:iam::222222222222:role/SpaAccountsManagementRole'
    assert toggles.role_arn_to_put_events == 'arn:aws:iam::333333333333:role/SpaPutEventsRole'
    assert toggles.role_name_to_manage_codebuild == 'SpaCodebuildManagementRole'


def test_set_from_yaml_invalid(toggles):
    with pytest.raises(AttributeError):
        Configuration.set_from_yaml(BytesIO(b'a: b\nc: d\n'))
