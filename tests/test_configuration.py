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
from types import SimpleNamespace

from resources import Configuration

import pytest
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
    assert builtins.toggles.aws_account is not None
    assert builtins.toggles.aws_environment is not None
    assert builtins.toggles.aws_region is not None

    with pytest.raises(FileNotFoundError):
        Configuration.initialize(stream='this*file*does*not*exist')


def test_set_default_values(toggles):
    Configuration.set_default_values()
    assert toggles.automation_role_name_to_manage_codebuild == 'AWSControlTowerExecution'
    assert toggles.automation_verbosity == 'INFO'


def test_set_from_settings(toggles):
    settings = dict(organizational_units=[dict(identifier='ou', budget_cost='500')])
    Configuration.set_from_settings(settings)
    assert toggles.organizational_units == {'ou': {'budget_cost': '500'}}


@pytest.mark.slow
def test_set_from_yaml(toggles):
    Configuration.set_from_yaml('tests/settings/sample_settings.yaml')
    assert toggles.automation_account_id == '123456789012'
    assert toggles.automation_cockpit_markdown_text.strip() == '# Sustainable Personal Accounts Dashboard\nCurrently under active development (beta)'
    assert toggles.automation_maintenance_window_expression == 'cron(0 18 ? * SAT *)'
    assert toggles.automation_region == 'eu-west-1'
    assert toggles.automation_role_arn_to_manage_accounts == 'arn:aws:iam::222222222222:role/SpaAccountsManagementRole'
    assert toggles.automation_role_name_to_manage_codebuild == 'AWSControlTowerExecution'
    assert toggles.automation_subscribed_email_addresses == ['finops_alerts@acme.com', 'cloud_operations@acme.com']
    assert toggles.automation_tags == {'CostCenter': 'shared'}
    assert toggles.automation_verbosity == 'ERROR'
    assert toggles.environment_identifier == 'SpaDemo'
    organizational_units = {
        'ou-1234': {
            'account_tags': {'CostCenter': 'abc', 'Sponsor': 'Foo Bar'},
            'budget_name': 'DataTeamBudget',
            'cost_budget': 500.0,
            'note': 'a container for some accounts',
            'preparation_variables': {'HELLO': 'WORLD'},
            'purge_variables': {'DRY_RUN': 'TRUE'}
        },
        'ou-5678': {
            'account_tags': {'CostCenter': 'xyz', 'Sponsor': 'Mister Jones'},
            'budget_name': 'DevelopmentTeamBudget',
            'cost_budget': 300,
            'note': 'another account container',
            'preparation_variables': {'HELLO': 'UNIVERSE'},
            'purge_variables': {'DRY_RUN': 'FALSE'}
        },
    }
    assert toggles.organizational_units == organizational_units
    assert toggles.worker_preparation_buildspec_template_file == 'tests/buildspec/preparation_account_template.yaml'
    assert toggles.worker_purge_buildspec_template_file == 'tests/buildspec/purge_account_template.yaml'


def test_set_from_yaml_invalid(toggles):
    with pytest.raises(AttributeError):
        Configuration.set_from_yaml(BytesIO(b'a: b\nc: d\n'))
