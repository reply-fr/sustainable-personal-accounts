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

import builtins
import os
import logging
from types import SimpleNamespace
import yaml

from aws_cdk import Environment


class Configuration:
    ''' toggles are accessible from every python modules '''

    ALLOWED_ATTRIBUTES = dict(
        accounts='list',
        automation_account_id='str',
        automation_cockpit_markdown_text='str',
        automation_maintenance_window_expression='str',
        automation_region='str',
        automation_role_arn_to_manage_accounts='str',
        automation_role_name_to_manage_codebuild='str',
        automation_tags='dict',
        automation_verbosity='str',
        environment_identifier='str',
        features_with_arm_architecture='bool',
        features_with_email_subscriptions_on_alerts='list',
        features_with_microsoft_webhook_on_alerts='str',
        organizational_units='list',
        worker_preparation_buildspec_template_file='str',
        worker_purge_buildspec_template_file='str',
    )

    ALLOWED_ACCOUNT_ATTRIBUTES = dict(
        account_tags='dict',
        identifier='str',
        note='str',
        preparation='dict',
        purge='dict'
    )

    ALLOWED_ORGANIZATIONAL_UNIT_ATTRIBUTES = dict(
        account_tags='dict',
        identifier='str',
        note='str',
        preparation='dict',
        purge='dict'
    )

    ALLOWED_PREPARATION_ATTRIBUTES = dict(
        feature='str',
        variables='dict'
    )

    ALLOWED_PURGE_ATTRIBUTES = dict(
        feature='str',
        variables='dict'
    )

    @staticmethod
    def expand_text(text, context: SimpleNamespace):
        ''' replace keywords in text with values found in context object '''
        for key in context.__dict__.keys():
            needle = "___{}___".format(key)
            index = text.find(needle)
            while (index >= 0):
                text = text[:index] + str(context.__dict__.get(key)) + text[index + len(needle):]
                index = text.find(needle)
        return text

    @classmethod
    def initialize(cls, stream=None, toggles=None):
        builtins.toggles = SimpleNamespace()
        toggles = toggles or builtins.toggles
        cls.set_default_values(toggles=toggles)
        if stream:
            cls.set_from_yaml(stream=stream, toggles=toggles)
        else:
            cls.set_from_yaml(stream=toggles.settings_file, toggles=toggles)
        cls.set_aws_environment(toggles=toggles)

    @staticmethod
    def set_default_values(toggles=None):
        toggles = toggles or builtins.toggles

        # identifier for this specific environment
        toggles.environment_identifier = "{}{}".format(
            os.environ.get('STACK_PREFIX', 'Spa'),
            os.environ.get('ENVIRONMENT', 'Alpha'))

        # use environment to locate settings file
        toggles.settings_file = os.environ.get('SETTINGS', 'settings.yaml')

        # the list of managed accounts and managed organizational units
        toggles.accounts = {}
        toggles.organizational_units = {}

        # other default values
        toggles.automation_cockpit_markdown_text = "# Sustainable Personal Accounts Dashboard\nCurrently under active development (alpha)"
        toggles.automation_role_name_to_manage_codebuild = 'AWSControlTowerExecution'
        toggles.automation_subscribed_email_addresses = []
        toggles.automation_tags = {}
        toggles.automation_verbosity = 'INFO'
        toggles.features_with_arm_architecture = False
        toggles.features_with_email_subscriptions_on_alerts = []
        toggles.features_with_microsoft_webhook_on_alerts = None

        for key in sorted(toggles.__dict__.keys()):
            value = toggles.__dict__.get(key)
            logging.debug("{0} = {1}".format(key, value))

    @classmethod
    def set_from_yaml(cls, stream, toggles=None):
        if type(stream) == str:
            with open(stream) as handle:
                logging.info(f"Loading configuration from '{stream}'")
                settings = yaml.safe_load(handle)
                cls.set_from_settings(settings=settings, toggles=toggles)
        else:
            settings = yaml.safe_load(stream)
            cls.set_from_settings(settings=settings, toggles=toggles)

    @classmethod
    def set_from_settings(cls, settings={}, toggles=None):
        for key in settings.keys():
            if type(settings[key]) == dict:
                for subkey in settings[key].keys():
                    flatten = "{0}_{1}".format(key, subkey)
                    value = settings[key].get(subkey)
                    cls.set_attribute(flatten, value, toggles=toggles)
            else:
                cls.set_attribute(key, settings[key], toggles=toggles)

    @classmethod
    def set_attribute(cls, key, value, toggles=None):
        cls.validate_attribute(key, value, context=cls.ALLOWED_ATTRIBUTES)
        if key == 'accounts':
            accounts = cls.transform_accounts(accounts=value)
            value = cls.set_accounts_default_values(accounts)
        elif key == 'organizational_units':
            units = cls.transform_organizational_units(units=value)
            value = cls.set_organizational_units_default_values(units)
        logging.debug("{0} = {1}".format(key, value))
        toggles = toggles or builtins.toggles
        setattr(toggles, key, value)

    @classmethod
    def validate_attribute(cls, key, value, context):
        kind = context.get(key)
        if kind:
            if (kind == 'bool') and not isinstance(value, bool):
                raise AttributeError(f"Invalid value for configuration attribute '{key}'")
            elif (kind == 'dict') and not isinstance(value, dict):
                raise AttributeError(f"Invalid value for configuration attribute '{key}'")
            elif (kind == 'int') and not isinstance(value, int):
                raise AttributeError(f"Invalid value for configuration attribute '{key}'")
            elif (kind == 'list') and not isinstance(value, list):
                raise AttributeError(f"Invalid value for configuration attribute '{key}'")
            elif (kind == 'str') and not isinstance(value, str):
                raise AttributeError(f"Invalid value for configuration attribute '{key}'")
        else:
            raise AttributeError(f"Unknown configuration attribute '{key}'")

    @classmethod
    def transform_accounts(cls, accounts):
        ''' make a dictionary out of a list of accounts, using identifier as key '''
        transformed = {}
        for account in accounts:
            cls.validate_account(account)
            key = account['identifier']
            transformed[key] = {k: account[k] for k in account.keys() if k != 'identifier'}
        return transformed

    @classmethod
    def transform_organizational_units(cls, units):
        ''' make a dictionary out of a list of OU, using identifier as key '''
        transformed = {}
        for unit in units:
            cls.validate_organizational_unit(unit)
            key = unit['identifier']
            transformed[key] = {k: unit[k] for k in unit.keys() if k != 'identifier'}
        return transformed

    @classmethod
    def set_accounts_default_values(cls, accounts):
        default = accounts.get('default', {})
        result = {}
        for account_id in accounts.keys():
            if account_id == 'default':
                continue
            values = accounts.get(account_id)
            updated = dict(preparation={}, purge={})
            updated['account_tags'] = default.get('account_tags', {})
            updated['account_tags'].update(values.get('account_tags', {}))
            updated['note'] = values.get('note', '')
            default_preparation = default.get('preparation', {})
            preparation = values.get('preparation', {})
            updated['preparation']['feature'] = preparation.get('feature', default_preparation.get('feature', 'disabled'))
            updated['preparation']['variables'] = default_preparation.get('variables', {})
            updated['preparation']['variables'].update(preparation.get('variables', {}))
            default_purge = default.get('purge', {})
            purge = values.get('purge', {})
            updated['purge']['feature'] = purge.get('feature', default_purge.get('feature', 'disabled'))
            updated['purge']['variables'] = default_purge.get('variables', {})
            updated['purge']['variables'].update(purge.get('variables', {}))
            result[account_id] = updated
        return result

    @classmethod
    def set_organizational_units_default_values(cls, units):
        default = units.get('default', {})
        result = {}
        for unit_id in units.keys():
            if unit_id == 'default':
                continue
            values = units.get(unit_id)
            updated = dict(preparation={}, purge={})
            updated['account_tags'] = default.get('account_tags', {})
            updated['account_tags'].update(values.get('account_tags', {}))
            updated['note'] = values.get('note', '')
            default_preparation = default.get('preparation', {})
            preparation = values.get('preparation', {})
            updated['preparation']['feature'] = preparation.get('feature', default_preparation.get('feature', 'disabled'))
            updated['preparation']['variables'] = default_preparation.get('variables', {})
            updated['preparation']['variables'].update(preparation.get('variables', {}))
            default_purge = default.get('purge', {})
            purge = values.get('purge', {})
            updated['purge']['feature'] = purge.get('feature', default_purge.get('feature', 'disabled'))
            updated['purge']['variables'] = default_purge.get('variables', {})
            updated['purge']['variables'].update(purge.get('variables', {}))
            result[unit_id] = updated
        return result

    @classmethod
    def validate_account(cls, account):
        if 'identifier' not in account.keys():
            raise AttributeError("Missing account 'identifier'")
        for key in account.keys():
            cls.validate_attribute(key, account.get(key), context=cls.ALLOWED_ACCOUNT_ATTRIBUTES)
        cls.validate_preparation_parameters(preparation=account.get('preparation', {}), target="account '{}'".format(account['identifier']))
        cls.validate_purge_parameters(purge=account.get('purge', {}), target="account '{}'".format(account['identifier']))

    @classmethod
    def validate_organizational_unit(cls, unit):
        if 'identifier' not in unit.keys():
            raise AttributeError("Missing organizational unit 'identifier'")
        for key in unit.keys():
            cls.validate_attribute(key, unit.get(key), context=cls.ALLOWED_ORGANIZATIONAL_UNIT_ATTRIBUTES)
        cls.validate_preparation_parameters(preparation=unit.get('preparation', {}), target="organizational unit '{}'".format(unit['identifier']))
        cls.validate_purge_parameters(purge=unit.get('purge', {}), target="organizational unit '{}'".format(unit['identifier']))

    @classmethod
    def validate_preparation_parameters(cls, preparation, target):
        for label in preparation.keys():
            if label not in ['feature', 'variables']:
                raise AttributeError(f"Unexpected preparation parameter '{label}' for {target}")

    @classmethod
    def validate_purge_parameters(cls, purge, target):
        for label in purge.keys():
            if label not in ['feature', 'variables']:
                raise AttributeError(f"Unexpected purge parameter '{label}' for {target}")

    @staticmethod
    def set_aws_environment(toggles=None):
        toggles = toggles or builtins.toggles

        account = os.environ.get('AWS_ACCOUNT', None)
        if account:
            logging.debug(f"using AWS_ACCOUNT = {account}")
        else:
            account = toggles.automation_account_id
            if account:
                logging.debug(f"using account = {account}")
            else:  # fall back to current aws profile
                account = os.environ.get('CDK_DEFAULT_ACCOUNT', None)
        toggles.automation_account_id = account

        region = os.environ.get('AWS_REGION', None)
        if region:
            logging.debug(f"using AWS_REGION = {region}")
        else:
            region = toggles.automation_region
            if region:
                logging.debug(f"using region = {region}")
            else:  # fall back to default region for current profile
                region = os.environ.get('CDK_DEFAULT_REGION', None)
        toggles.automation_region = region

        logging.info("AWS environment is account '{0}' and region '{1}'".format(toggles.automation_account_id,
                                                                                toggles.automation_region))
        toggles.aws_environment = Environment(account=toggles.automation_account_id, region=toggles.automation_region)
