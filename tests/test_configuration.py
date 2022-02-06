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
import os
import pytest
from types import SimpleNamespace

from code.configuration import Configuration


# pytestmark = pytest.mark.wip


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
def test_initialize():
    Configuration.initialize()
    assert builtins.toggles.dry_run is False
    assert builtins.toggles.aws_account is not None
    assert builtins.toggles.aws_environment is not None
    assert builtins.toggles.aws_region is not None

    Configuration.initialize(dry_run=True)
    assert builtins.toggles.dry_run is True

    with pytest.raises(FileNotFoundError):
        Configuration.initialize(stream='this*file*does*not*exist')


def test_set_default_values(toggles):
    Configuration.set_default_values()


def test_set_from_environment(toggles):
    environ = dict(
        active_directory_domain_credentials="where-my-secret-is",
        TRUSTED_PEER='4.3.2.1/32',
        NOT_MAPPED_VARIABLE="what'up Doc?",
        NONE_VARIABLE=None,
        NULL_VARIABLE='')

    Configuration.set_from_environment(environ=environ)
    assert toggles.__dict__.get('active_directory_domain_credentials') is None

    mapping = dict(
        active_directory_domain_credentials='active_directory_domain_credentials',
        inexistant_variable="*THIS*DOES*NOT*EXIST*IN*ENVIRONMENT",
        none_variable='NONE_VARIABLE',
        null_variable='NULL_VARIABLE')
    Configuration.set_from_environment(environ=environ, mapping=mapping)
    assert toggles.active_directory_domain_credentials == "where-my-secret-is"
    with pytest.raises(Exception):
        assert toggles.inexistant_variable is None
    with pytest.raises(Exception):
        assert toggles.none_variable is None
    assert toggles.null_variable == ''


def test_set_from_settings(toggles):
    settings = dict(active_directory=dict(specific_parameter="foo bar"))
    Configuration.set_from_settings(settings)
    assert toggles.active_directory_specific_parameter == "foo bar"
    with pytest.raises(Exception):
        assert toggles.inexistant_toggle is None


@pytest.mark.slow
def test_set_from_yaml(toggles):
    Configuration.set_from_yaml(BytesIO(b'a: b\nc: d\n'))
    assert toggles.a == 'b'  # 1
    assert toggles.c == 'd'  # 2

    Configuration.set_from_yaml('tests/settings/sample_settings.yaml')
    assert toggles.organisational_units_assigned_accounts_identifier == 'ou-5678'
    assert toggles.organisational_units_expired_accounts_identifier == 'ou-efghij'
    assert toggles.organisational_units_released_accounts_identifier == 'ou-90abcd'
    assert toggles.organisational_units_vanilla_accounts_identifier == 'ou-1234'
