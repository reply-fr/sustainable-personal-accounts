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

from cdk import Configuration

pytestmark = pytest.mark.wip


@pytest.fixture
def toggles():
    return SimpleNamespace()


@pytest.mark.unit_tests
def test_expand_text(toggles):
    text = 'this is some sample text with ___parameter___ to replace'
    toggles.parameter = '=value='
    test = Configuration.expand_text(text, toggles)
    assert test == 'this is some sample text with =value= to replace'


@pytest.mark.unit_tests
@patch.dict(os.environ, dict(AWS_ACCOUNT="012345678901", AWS_REGION="eu-west-9"))
def test_initialize(toggles):

    Configuration.initialize(stream='fixtures/settings/settings.yaml', toggles=toggles)
    assert toggles.automation_account_id == "012345678901"
    assert toggles.automation_region == "eu-west-9"
    assert toggles.aws_environment is not None

    with pytest.raises(FileNotFoundError):
        Configuration.initialize(stream='this*file*does*not*exist')


@pytest.mark.unit_tests
@patch.dict(os.environ, dict(AWS_ACCOUNT="012345678901", AWS_REGION="eu-west-9"))
def test_initialize_on_malformed_settings_file(toggles):

    with pytest.raises(AttributeError):
        Configuration.initialize(stream='fixtures/settings/settings-with-old-default-settings.yaml', toggles=toggles)


@pytest.mark.unit_tests
@patch.dict(os.environ, {}, clear=True)
def test_set_aws_environment(toggles):
    Configuration.set_from_yaml('fixtures/settings/settings.yaml', toggles=toggles)
    Configuration.set_aws_environment(toggles=toggles)
    assert toggles.automation_account_id == "123456789012"
    assert toggles.automation_region == "eu-west-1"
    assert toggles.aws_environment is not None


@pytest.mark.unit_tests
@patch.dict(os.environ, dict(AWS_ACCOUNT="987654321098", AWS_REGION="eu-central-1"))
def test_set_aws_environment_from_environment_variables(toggles):
    logging.debug("here AWS_ACCOUNT={}".format(os.environ.get("AWS_ACCOUNT", 'not found')))
    Configuration.set_from_yaml('fixtures/settings/settings.yaml', toggles=toggles)
    Configuration.set_aws_environment(toggles=toggles)
    assert toggles.automation_account_id == "987654321098"
    assert toggles.automation_region == "eu-central-1"
    assert toggles.aws_environment is not None


@pytest.mark.unit_tests
@patch.dict(os.environ, dict(CDK_DEFAULT_ACCOUNT="012345678901", CDK_DEFAULT_REGION="eu-west-9"), clear=True)
def test_set_aws_environment_from_cdk_runtime(toggles):
    Configuration.set_from_yaml('fixtures/settings/settings.yaml', toggles=toggles)
    toggles.automation_account_id = None
    toggles.automation_region = None
    Configuration.set_aws_environment(toggles=toggles)
    assert toggles.automation_account_id == "012345678901"
    assert toggles.automation_region == "eu-west-9"
    assert toggles.aws_environment is not None


@pytest.mark.unit_tests
def test_set_default_values(toggles):
    Configuration.set_default_values(toggles=toggles)
    assert toggles.automation_role_name_to_manage_codebuild == 'AWSControlTowerExecution'
    assert toggles.automation_verbosity == 'INFO'
    assert toggles.features_with_arm_architecture is False
    assert toggles.features_with_csv_files == []
    assert toggles.features_with_email_subscriptions_on_alerts == []
    assert toggles.features_with_microsoft_webhook_on_alerts is None
    assert toggles.features_with_tag_prefix == 'account-'
    assert toggles.features_with_cost_management_tag is False
    assert toggles.metering_records_datastore == 'SpaRecordsTable'
    assert toggles.metering_records_ttl_in_seconds == 31622400
    assert toggles.metering_shadows_datastore == 'SpaShadowsTable'
    assert toggles.metering_shadows_ttl_in_seconds == 15811200
    assert toggles.metering_transactions_datastore == 'SpaTransactionsTable'
    assert toggles.metering_transactions_ttl_in_seconds == 3600


@pytest.mark.unit_tests
def test_set_from_settings(toggles):
    settings = dict(defaults=dict(note='a note'), organizational_units=[dict(identifier='ou-1234', preparation=dict(variables=dict(BUDGET_AMOUNT='500')))])
    Configuration.set_from_settings(settings, toggles=toggles)
    assert toggles.organizational_units == {'ou-1234': {'account_tags': {},
                                                        'identifier': 'ou-1234',
                                                        'note': 'a note',
                                                        'preparation': {'feature': 'disabled', 'variables': {'BUDGET_AMOUNT': '500'}},
                                                        'purge': {'feature': 'disabled', 'variables': {}}}}


@pytest.mark.unit_tests
def test_set_from_settings_with_default_values(toggles):
    settings = dict(
        defaults=dict(account_tags=dict(a='a', b='b'),
                      note='some note',
                      preparation=dict(feature='disabled', variables=dict(BUDGET_AMOUNT='500')),
                      purge=dict(feature='disabled', variables=dict([('operations-class', 'unknown')]))),
        organizational_units=[dict(identifier='ou-1234',
                                   account_tags=dict(b='z', c='c'),
                                   note='ou description',
                                   preparation=dict(feature='enabled', variables=dict(BUDGET_THRESHOLD='80')),
                                   purge=dict(feature='enabled', variables=dict([('operations-class', 'sandbox')])))],
        accounts=[dict(identifier='123456789012',
                       account_tags=dict(b='z', c='c'),
                       note='account description',
                       preparation=dict(feature='enabled', variables=dict(BUDGET_THRESHOLD='800')),
                       purge=dict(feature='disabled', variables=dict([('operations-class', 'committed')])))],
        features=dict(with_arm_architecture=True))
    Configuration.set_from_settings(settings, toggles=toggles)
    assert toggles.defaults == {'account_tags': {'a': 'a', 'b': 'b'},
                                'note': 'some note',
                                'preparation': {'feature': 'disabled', 'variables': {'BUDGET_AMOUNT': '500'}},
                                'purge': {'feature': 'disabled', 'variables': {'operations-class': 'unknown'}}}
    assert toggles.organizational_units == {'ou-1234': {'account_tags': {'a': 'a', 'b': 'z', 'c': 'c'},
                                                        'identifier': 'ou-1234',
                                                        'note': 'ou description',
                                                        'preparation': {'feature': 'enabled', 'variables': {'BUDGET_AMOUNT': '500', 'BUDGET_THRESHOLD': '80'}},
                                                        'purge': {'feature': 'enabled', 'variables': {'operations-class': 'sandbox'}}}}
    assert toggles.accounts == {'123456789012': {'account_tags': {'a': 'a', 'b': 'z', 'c': 'c'},
                                                 'identifier': '123456789012',
                                                 'note': 'account description',
                                                 'preparation': {'feature': 'enabled', 'variables': {'BUDGET_AMOUNT': '500', 'BUDGET_THRESHOLD': '800'}},
                                                 'purge': {'feature': 'disabled', 'variables': {'operations-class': 'committed'}}}}


@pytest.mark.integration_tests
@pytest.mark.slow
def test_set_from_yaml(toggles):
    Configuration.set_from_yaml('fixtures/settings/settings.yaml', toggles=toggles)
    assert toggles.automation_account_id == '123456789012'
    assert toggles.automation_cockpit_markdown_text.strip() == '# Sustainable Personal Accounts Dashboard\nCurrently under active development (beta)'
    assert toggles.automation_maintenance_window_expression == 'cron(0 18 ? * SAT *)'
    assert toggles.automation_region == 'eu-west-1'
    assert toggles.automation_role_arn_to_manage_accounts == 'arn:aws:iam::222222222222:role/SpaAccountsManagementRole'
    assert toggles.automation_role_name_to_manage_codebuild == 'AWSControlTowerExecution'
    assert toggles.automation_tags == {'account-manager': 'john.foo@acme.com', 'cost-imputation': 'shared'}
    assert toggles.automation_verbosity == 'ERROR'
    assert toggles.environment_identifier == 'SpaDemo'
    assert list(toggles.organizational_units.keys()) == ['ou-1234', 'ou-5678']
    assert toggles.worker_preparation_buildspec_template_file == 'fixtures/buildspec/preparation_account_template.yaml'
    assert toggles.worker_purge_buildspec_template_file == 'fixtures/buildspec/purge_account_with_awsweeper_template.yaml'
    assert toggles.features_with_arm_architecture is True
    assert toggles.features_with_email_subscriptions_on_alerts == ['finops_alerts@acme.com', 'cloud_operations@acme.com']
    assert toggles.features_with_microsoft_webhook_on_alerts == 'https://acme.webhook.office.com/webhookb2/892ca8xf-9423'
    assert toggles.features_with_tag_prefix == 'account-'
    assert toggles.features_with_cost_management_tag == 'cost-center'
    assert toggles.metering_records_datastore == 'SpaRecordsTable'
    assert toggles.metering_records_ttl_in_seconds == 31622400
    assert toggles.metering_shadows_datastore == 'SpaShadowsTable'
    assert toggles.metering_shadows_ttl_in_seconds == 15811200
    assert toggles.metering_transactions_datastore == 'SpaTransactionsTable'
    assert toggles.metering_transactions_ttl_in_seconds == 900


@pytest.mark.unit_tests
def test_set_from_invalid_yaml(toggles):
    with pytest.raises(AttributeError):
        Configuration.set_from_yaml(BytesIO(b'a: b\nc: d\n'))


@pytest.mark.integration_tests
@pytest.mark.slow
def test_set_from_csv_files(toggles):
    Configuration.set_from_yaml('fixtures/settings/settings-with-csv-files.yaml', toggles=toggles)
    assert toggles.automation_account_id == '123456789012'
    assert toggles.features_with_csv_files == ['finops-setup.csv', 'security-setup.csv']
    assert list(toggles.accounts.keys()) == ['123456789012', '210987654321', '456789012345', '789012345678']

    assert toggles.accounts['123456789012'] == {'identifier': '123456789012',
                                                'note': 'one specific account',                                        # accounts
                                                'account_tags': {'ServiceNow Domain': 'CloudOps',                      # security
                                                                 'account-manager': 'alice@acme.com',                  # accounts
                                                                 'cost-center': 'ApplicationOne Department',           # accounts overwritten by finops
                                                                 'cost-imputation': 'SB-123',                          # accounts
                                                                 'managed-by': 'SPA'},                                 # default
                                                'preparation': {'feature': 'enabled',                                  # accounts
                                                                'variables': {'ALERT_THRESHOLD': 90,                   # accounts
                                                                              'BUDGET_AMOUNT': '2000',                 # accounts overwritten by finops
                                                                              'BUDGET_NAME': 'SpecificAliceBudget'}},  # accounts
                                                'purge': {'feature': 'disabled',                                       # default
                                                          'variables': {'MAXIMUM_AGE': '3M',                           # finops
                                                                        'PURGE_MODE': '--dry-run',                     # default
                                                                        'TAG_KEY': 'purge',                            # default
                                                                        'TAG_VALUE': 'me'}}}                           # default

    assert toggles.accounts['210987654321'] == {'identifier': '210987654321',
                                                'note': 'another specific account',                                   # accounts
                                                'account_tags': {'account-manager': 'bob@acme.com',                   # accounts
                                                                 'cost-center': 'Bob',                                # accounts
                                                                 'cost-imputation': 'SB-456',                         # accounts
                                                                 'managed-by': 'SPA'},                                # default
                                                'preparation': {'feature': 'enabled',                                 # accounts
                                                                'variables': {'ALERT_THRESHOLD': 90,                  # accounts
                                                                              'BUDGET_AMOUNT': 4000,                  # accounts
                                                                              'BUDGET_NAME': 'SpecificBobBudget'}},   # accounts
                                                'purge': {'feature': 'disabled',                                      # default
                                                          'variables': {'MAXIMUM_AGE': '9M',                          # default
                                                                        'PURGE_MODE': '--dry-run',                    # default
                                                                        'TAG_KEY': 'purge',                           # default
                                                                        'TAG_VALUE': 'me'}}}                          # default

    assert toggles.accounts['456789012345'] == {'identifier': '456789012345',
                                                'note': 'An alien account',                                           # finops
                                                'account_tags': {'managed-by': 'SPA',                                 # default
                                                                 'cost-center': 'Customer Service',                   # finops
                                                                 'ServiceNow Domain': 'CustomerServiceDomain'},       # security
                                                'preparation': {'feature': 'disabled',                                # default
                                                                'variables': {'ALERT_THRESHOLD': 80,                  # default
                                                                              'BUDGET_AMOUNT': '3000',                # finops
                                                                              'BUDGET_NAME': 'SpaBudget'}},           # default
                                                'purge': {'feature': 'disabled',                                      # default
                                                          'variables': {'MAXIMUM_AGE': '6M',                          # finops
                                                                        'PURGE_MODE': '--dry-run',                    # default
                                                                        'TAG_KEY': 'purge',                           # default
                                                                        'TAG_VALUE': 'me'}}}                          # default

    assert toggles.accounts['789012345678'] == {'identifier': '789012345678',
                                                'note': 'A third-party added recently',                               # finops
                                                'account_tags': {'managed-by': 'SPA',                                 # default
                                                                 'cost-center': 'Financial Department',               # finops
                                                                 'ServiceNow Domain': 'FinanceResponders'},           # security
                                                'preparation': {'feature': 'disabled',                                # default
                                                                'variables': {'ALERT_THRESHOLD': 80,                  # default
                                                                              'BUDGET_AMOUNT': '600',                 # finops
                                                                              'BUDGET_NAME': 'SpaBudget'}},           # default
                                                'purge': {'feature': 'disabled',                                      # default
                                                          'variables': {'MAXIMUM_AGE': '10Y',                         # finops
                                                                        'PURGE_MODE': '--dry-run',                    # default
                                                                        'TAG_KEY': 'purge',                           # default
                                                                        'TAG_VALUE': 'me'}}}                          # default


@pytest.mark.unit_tests
def test_transform_list_to_dictionary():

    input = [dict(identifier='a', attribute='a'), dict(identifier='b', attribute='b')]
    output = Configuration.transform_list_to_dictionary(input)
    assert output == {'a': {'attribute': 'a', 'identifier': 'a'},
                      'b': {'attribute': 'b', 'identifier': 'b'}}

    with pytest.raises(AttributeError):
        input = [dict(identifier='a', attribute='a'), dict(identifier='a', attribute='b')]
        output = Configuration.transform_list_to_dictionary(input)


@pytest.mark.unit_tests
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


@pytest.mark.unit_tests
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


@pytest.mark.unit_tests
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
