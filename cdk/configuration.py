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
from csv import DictReader
import json
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
        defaults='dict',
        environment_identifier='str',
        features_with_arm_architecture='bool',
        features_with_cost_email_recipients='list',
        features_with_cost_extra_currencies='list',
        features_with_cost_management_tag='str',
        features_with_csv_files='list',
        features_with_email_subscriptions_on_alerts='list',
        features_with_end_user_documents='dict',
        features_with_microsoft_webhook_on_alerts='str',
        features_with_origin_email_recipient='str',
        features_with_response_plan_arn='str',
        features_with_tag_prefix='str',
        metering_activities_datastore='str',
        metering_activities_ttl_in_seconds='int',
        metering_shadows_datastore='str',
        metering_shadows_ttl_in_seconds='int',
        metering_transactions_datastore='str',
        metering_transactions_ttl_in_seconds='int',
        organizational_units='list',
        reporting_activities_prefix='str',
        reporting_costs_prefix='str',
        reporting_costs_markdown_template='str',
        reporting_exceptions_prefix='str',
        reporting_inventories_prefix='str',
        worker_preparation_buildspec_template_file='str',
        worker_purge_buildspec_template_file='str',
    )

    ALLOWED_ACCOUNT_ATTRIBUTES = dict(
        account_tags='dict',
        identifier='str',
        note='str',
        preparation='dict',
        purge='dict',
        unset_tags='list'
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
        toggles.state_tag = toggles.features_with_tag_prefix + 'state'  # for EventBridge rule

    @staticmethod
    def set_default_values(toggles=None):
        toggles = toggles or builtins.toggles

        # identifier for this specific environment
        toggles.environment_identifier = "{}{}".format(
            os.environ.get('STACK_PREFIX', 'Spa'),
            os.environ.get('ENVIRONMENT', 'Beta'))

        # use environment to locate settings file
        toggles.settings_file = os.environ.get('SETTINGS', 'settings.yaml')

        # the list of managed accounts and of managed organizational units
        toggles.accounts = {}
        toggles.organizational_units = {}

        # default settings for accounts
        toggles.defaults = {}

        # other default values
        toggles.automation_cockpit_markdown_text = "# Sustainable Personal Accounts Dashboard\nCurrently under active development (beta)"
        toggles.automation_role_name_to_manage_codebuild = 'AWSControlTowerExecution'
        toggles.automation_subscribed_email_addresses = []
        toggles.automation_tags = {}
        toggles.automation_verbosity = 'INFO'
        toggles.features_with_arm_architecture = False
        toggles.features_with_cost_email_recipients = None
        toggles.features_with_cost_extra_currencies = None
        toggles.features_with_cost_management_tag = None
        toggles.features_with_csv_files = None
        toggles.features_with_email_subscriptions_on_alerts = None
        toggles.features_with_end_user_documents = None
        toggles.features_with_microsoft_webhook_on_alerts = None
        toggles.features_with_origin_email_recipient = None
        toggles.features_with_response_plan_arn = ''
        toggles.features_with_tag_prefix = 'account-'
        toggles.metering_activities_datastore = "ActivitiesTable"        # will be prefixed with environment identifier
        toggles.metering_activities_ttl_in_seconds = 366 * 24 * 60 * 60  # 1 year TTL
        toggles.metering_shadows_datastore = "ShadowsTable"              # will be prefixed with environment identifier
        toggles.metering_shadows_ttl_in_seconds = 183 * 24 * 60 * 60     # 6 months TTL
        toggles.metering_transactions_datastore = "TransactionsTable"    # will be prefixed with environment identifier
        toggles.metering_transactions_ttl_in_seconds = 3 * 60 * 60       # 3 hours TTL
        toggles.reporting_activities_prefix = 'SpaReports/Activities'
        toggles.reporting_costs_prefix = 'SpaReports/Costs'
        toggles.reporting_costs_markdown_template = "You will find attached cloud cost reports for {month}"
        toggles.reporting_exceptions_prefix = 'SpaReports/Exceptions'
        toggles.reporting_inventories_prefix = 'SpaReports/Inventories'

        for key in sorted(toggles.__dict__.keys()):
            value = toggles.__dict__.get(key)
            logging.debug("{0} = {1}".format(key, value))

    @classmethod
    def set_from_yaml(cls, stream, toggles=None):
        if type(stream) == str:
            with open(stream) as handle:
                logging.info(f"Loading configuration from '{stream}'")
                settings = yaml.safe_load(handle)
                cls.set_from_settings(settings=settings, toggles=toggles, path=os.path.split(stream)[0])
        else:
            settings = yaml.safe_load(stream)
            cls.set_from_settings(settings=settings, toggles=toggles)

    @classmethod
    def set_from_settings(cls, settings={}, toggles=None, path=None):
        if 'defaults' in settings.keys():
            cls.set_attribute('defaults', settings['defaults'], toggles=toggles)

        toggles.features_with_csv_files = None
        toggles.features_with_end_user_documents = None
        for key in settings.keys():
            if key == 'defaults':
                continue
            elif type(settings[key]) == dict:
                for subkey in settings[key].keys():
                    flatten = "{0}_{1}".format(key, subkey)
                    value = settings[key].get(subkey)
                    cls.set_attribute(flatten, value, toggles=toggles)
            else:
                cls.set_attribute(key, settings[key], toggles=toggles)

        if toggles.features_with_csv_files:
            for file in toggles.features_with_csv_files:
                cls.set_from_csv_file(os.path.join(path or '.', file), toggles=toggles)

    @classmethod
    def set_from_csv_file(cls, file, toggles=None):
        logging.info(f"Loading CSV configuration from '{file}'")
        with open(file) as stream:
            for item in DictReader(stream):
                cls.set_from_account_settings(settings=item, toggles=toggles)

    @classmethod
    def set_from_account_settings(cls, settings, toggles=None):
        logging.debug(settings)

        other = {}
        tags = {}
        preparation = {}
        purge = {}

        expressions = dict(Account="other['account'] = value",
                           Note="other['note'] = value",
                           Tag="tags[key] = value",
                           Preparation="preparation[key] = value",
                           Purge="purge[key] = value")

        for key, value in settings.items():
            parts = key.split(':', 1)
            label = parts[0].strip()
            key = parts[1].strip() if len(parts) > 1 else None
            value = value.strip()
            exec(expressions[label])

        if not other.get('account'):
            raise ValueError("Missing value in column 'Account'")
        account = other['account']

        configuration = toggles.accounts.get(account) or json.loads(json.dumps(toggles.defaults))  # complete copy of default dict
        configuration['identifier'] = account
        if other.get('note'):
            configuration['note'] = other['note']
        configuration['account_tags'].update(tags)
        configuration['preparation']['variables'].update(preparation)
        configuration['purge']['variables'].update(purge)
        toggles.accounts[account] = configuration

    @classmethod
    def set_attribute(cls, key, value, toggles=None):
        toggles = toggles or builtins.toggles
        cls.validate_attribute(key, value, context=cls.ALLOWED_ATTRIBUTES)
        if key == 'accounts':
            for account in value:
                cls.set_configuration_item_default_attributes(item=account, defaults=toggles.defaults)
                cls.validate_account(account)
            value = cls.transform_list_to_dictionary(value)
        elif key == 'organizational_units':
            for unit in value:
                cls.set_configuration_item_default_attributes(item=unit, defaults=toggles.defaults)
                cls.validate_organizational_unit(unit)
            value = cls.transform_list_to_dictionary(value)
        logging.debug("{0} = {1}".format(key, value))
        setattr(toggles, key, value)

    @classmethod
    def set_configuration_item_default_attributes(cls, item, defaults):
        for attribute in ['account_tags', 'preparation', 'purge']:
            if attribute not in defaults.keys():
                defaults[attribute] = {}
            if attribute not in item.keys():
                item[attribute] = {}

        missing = {k: v for k, v in defaults.items() if k not in item.keys()}
        item.update(missing)

        missing = {k: v for k, v in defaults['account_tags'].items() if k not in item['account_tags'].keys()}
        item['account_tags'].update(missing)

        for attribute in ['preparation', 'purge']:
            cls.set_configuration_item_worker_attributes(item[attribute], defaults[attribute])

    @classmethod
    def set_configuration_item_worker_attributes(cls, item, defaults):
        if 'feature' not in defaults.keys():
            defaults['feature'] = 'disabled'
        if 'variables' not in defaults.keys():
            defaults['variables'] = {}
        if 'feature' not in item.keys():
            item['feature'] = defaults['feature']
        if 'variables' not in item.keys():
            item['variables'] = {}

        missing = {k: v for k, v in defaults['variables'].items() if k not in item['variables'].keys()}
        item['variables'].update(missing)

    @classmethod
    def transform_list_to_dictionary(cls, items):
        ''' make a dictionary out of a list, using identifier as key '''
        transformed = {}
        for item in items:
            key = item['identifier']
            if key in transformed.keys():
                raise AttributeError(f"Duplicate identifier'{key}' in settings")
            transformed[key] = item.copy()
        return transformed

    @classmethod
    def validate_account(cls, account):
        if 'identifier' not in account.keys():
            raise AttributeError("Missing account 'identifier'")
        if (not account['identifier'].isdigit()) or (len(account['identifier']) != 12):
            raise AttributeError("The identifier '{}' is not valid for an AWS account".format(account['identifier']))
        cls.validate_configuration_item(item=account)

    @classmethod
    def validate_organizational_unit(cls, unit):
        if 'identifier' not in unit.keys():
            raise AttributeError("Missing organizational unit 'identifier'")
        if not unit['identifier'].startswith('ou-'):
            raise AttributeError("The identifier '{}' is not valid for an AWS Organizational Unit".format(unit['identifier']))
        cls.validate_configuration_item(item=unit)

    @classmethod
    def validate_configuration_item(cls, item):
        for key in item.keys():
            cls.validate_attribute(key, item.get(key), context=cls.ALLOWED_ACCOUNT_ATTRIBUTES)
        cls.validate_preparation_attributes(item)
        cls.validate_purge_attributes(item)

    @classmethod
    def validate_attribute(cls, key, value, context):
        kind = context.get(key)
        if value:
            if kind:
                if (kind == 'bool') and not isinstance(value, bool):
                    raise AttributeError(f"Invalid type '{type(value).__name__}' for configuration attribute '{key}'")
                elif (kind == 'dict') and not isinstance(value, dict):
                    raise AttributeError(f"Invalid type '{type(value).__name__}' for configuration attribute '{key}'")
                elif (kind == 'int') and not isinstance(value, int):
                    raise AttributeError(f"Invalid type '{type(value).__name__}' for configuration attribute '{key}'")
                elif (kind == 'list') and not isinstance(value, list):
                    raise AttributeError(f"Invalid type '{type(value).__name__}' for configuration attribute '{key}'")
                elif (kind == 'str') and not isinstance(value, str):
                    raise AttributeError(f"Invalid type '{type(value).__name__}' for configuration attribute '{key}'")
            else:
                raise AttributeError(f"Unknown configuration attribute '{key}'")

    @classmethod
    def validate_preparation_attributes(cls, item):
        preparation = item.get('preparation', {})
        for label in preparation.keys():
            if label not in ['feature', 'variables']:
                identifier = item['identifier']
                raise AttributeError(f"Unexpected preparation parameter '{label}' for {identifier}")

    @classmethod
    def validate_purge_attributes(cls, item):
        purge = item.get('purge', {})
        for label in purge.keys():
            if label not in ['feature', 'variables']:
                identifier = item['identifier']
                raise AttributeError(f"Unexpected purge parameter '{label}' for {identifier}")

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
