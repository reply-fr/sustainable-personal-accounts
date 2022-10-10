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

from io import BytesIO
from unittest.mock import patch
import os
import pytest
from types import SimpleNamespace

from resources import Configuration

# pytestmark = pytest.mark.wip


@pytest.fixture
def toggles():
    return SimpleNamespace()


def test_expand_text(toggles):
    text = 'this is some sample text with ___parameter___ to replace'
    toggles.parameter = '=value='
    test = Configuration.expand_text(text, toggles)
    assert test == 'this is some sample text with =value= to replace'


@patch.dict(os.environ, dict(AWS_ACCOUNT="012345678901", AWS_REGION="eu-west-9"))
def test_initialize(toggles):

    Configuration.initialize(stream='fixtures/settings/settings.yaml', toggles=toggles)
    assert toggles.automation_account_id == "012345678901"
    assert toggles.automation_region == "eu-west-9"
    assert toggles.aws_environment is not None

    with pytest.raises(FileNotFoundError):
        Configuration.initialize(stream='this*file*does*not*exist')


def test_set_aws_environment(toggles):
    Configuration.set_from_yaml('fixtures/settings/settings.yaml', toggles=toggles)
    Configuration.set_aws_environment(toggles=toggles)
    assert toggles.automation_account_id == "123456789012"
    assert toggles.automation_region == "eu-west-1"
    assert toggles.aws_environment is not None


@patch.dict(os.environ, dict(AWS_ACCOUNT="987654321098", AWS_REGION="eu-central-1"))
def test_set_aws_environment_from_environment_variables(toggles):
    logging.debug("here AWS_ACCOUNT={}".format(os.environ.get("AWS_ACCOUNT", 'not found')))
    Configuration.set_from_yaml('fixtures/settings/settings.yaml', toggles=toggles)
    Configuration.set_aws_environment(toggles=toggles)
    assert toggles.automation_account_id == "987654321098"
    assert toggles.automation_region == "eu-central-1"
    assert toggles.aws_environment is not None


@patch.dict(os.environ, dict(CDK_DEFAULT_ACCOUNT="012345678901", CDK_DEFAULT_REGION="eu-west-9"))
def test_set_aws_environment_from_cdk_runtime(toggles):
    Configuration.set_from_yaml('fixtures/settings/settings.yaml', toggles=toggles)
    print(toggles)
    toggles.automation_account_id = None
    toggles.automation_region = None
    Configuration.set_aws_environment(toggles=toggles)
    assert toggles.automation_account_id == "012345678901"
    assert toggles.automation_region == "eu-west-9"
    assert toggles.aws_environment is not None


def test_set_default_values(toggles):
    Configuration.set_default_values(toggles=toggles)
    assert toggles.automation_role_name_to_manage_codebuild == 'AWSControlTowerExecution'
    assert toggles.automation_verbosity == 'INFO'


def test_set_from_settings(toggles):
    settings = dict(organizational_units=[dict(identifier='ou', preparation=dict(variables=dict(BUDGET_AMOUNT='500')))])
    Configuration.set_from_settings(settings, toggles=toggles)
    assert toggles.organizational_units == {'ou': {'account_tags': {},
                                                   'note': '',
                                                   'preparation': {'feature': 'disabled', 'variables': {'BUDGET_AMOUNT': '500'}},
                                                   'purge': {'feature': 'disabled', 'variables': {}}}}


def test_set_from_settings_with_default_values(toggles):
    settings = dict(organizational_units=[
        dict(identifier='default',
             account_tags=dict(a='a', b='b'),
             note='some note',
             preparation=dict(feature='disabled', variables=dict(BUDGET_AMOUNT='500')),
             purge=dict(feature='disabled', variables=dict(KEY='a key', MAX_AGE='3w'))),
        dict(identifier='ou',
             account_tags=dict(b='z', c='c'),
             note='ou description',
             preparation=dict(feature='enabled', variables=dict(BUDGET_THRESHOLD='80')),
             purge=dict(feature='enabled', variables=dict(KEY='another key', VALUE='value')))],
        features=dict(with_arm=True))
    Configuration.set_from_settings(settings, toggles=toggles)
    assert toggles.organizational_units == {'ou': {'account_tags': {'a': 'a', 'b': 'z', 'c': 'c'},
                                                   'note': 'ou description',
                                                   'preparation': {'feature': 'enabled', 'variables': {'BUDGET_AMOUNT': '500', 'BUDGET_THRESHOLD': '80'}},
                                                   'purge': {'feature': 'enabled', 'variables': {'KEY': 'another key', 'MAX_AGE': '3w', 'VALUE': 'value'}}}}


@pytest.mark.slow
def test_set_from_yaml(toggles):
    Configuration.set_from_yaml('fixtures/settings/settings.yaml', toggles=toggles)
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
    assert list(toggles.organizational_units.keys()) == ['ou-1234', 'ou-5678']
    assert toggles.worker_preparation_buildspec_template_file == 'fixtures/buildspec/preparation_account_template.yaml'
    assert toggles.worker_purge_buildspec_template_file == 'fixtures/buildspec/purge_account_with_awsweeper_template.yaml'
    assert toggles.features_with_arm is True


def test_set_from_yaml_invalid(toggles):
    with pytest.raises(AttributeError):
        Configuration.set_from_yaml(BytesIO(b'a: b\nc: d\n'))


def test_validate_organizational_unit():
    ou = {
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
    Configuration.validate_organizational_unit(ou)


def test_validate_organizational_unit_on_invalid_keys():
    ou = {
        'identifier': 'ou-5678',
        'account_tags': {'CostCenter': 'xyz', 'Sponsor': 'Mister Jones'},
        'budget_name': 'DevelopmentTeamBudget',
        'cost_budget': 300,
        'note': 'another account container',
        'preparation_variables': {'HELLO': 'UNIVERSE'},
        'purge_variables': {'DRY_RUN': 'FALSE'},
        'skipped': ['preparation', 'purge']
    }
    with pytest.raises(AttributeError):
        Configuration.validate_organizational_unit(ou)


def test_validate_organizational_unit_on_missing_identifier():
    ou = {
        'account_tags': {'CostCenter': 'abc', 'Sponsor': 'Foo Bar'},
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
    with pytest.raises(AttributeError):
        Configuration.validate_organizational_unit(ou)
