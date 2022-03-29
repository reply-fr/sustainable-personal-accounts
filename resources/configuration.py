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
import boto3


class Configuration:
    ''' toggles are accessible from every python modules '''

    ALLOWED_ATTRIBUTES = dict(
        automation_account_id='str',
        automation_cockpit_markdown_text='str',
        automation_maintenance_window_expression='str',
        automation_region='str',
        automation_role_arn_to_manage_accounts='str',
        automation_role_name_to_manage_codebuild='str',
        automation_subscribed_email_addresses='list',
        automation_tags='dict',
        automation_verbosity='str',
        environment_identifier='str',
        organizational_units='list',
        worker_preparation_buildspec_template_file='str',
        worker_purge_buildspec_template_file='str',
    )

    @staticmethod
    def expand_text(text, context: SimpleNamespace):
        ''' replace keywords in text with values found in context object '''
        for key in context.__dict__.keys():
            needle = "___{}___".format(key)
            index = text.find(needle)
            while(index >= 0):
                text = text[:index] + str(context.__dict__.get(key)) + text[index + len(needle):]
                index = text.find(needle)
        return text

    @classmethod
    def initialize(cls, stream=None, features: SimpleNamespace = None):
        builtins.toggles = SimpleNamespace()
        cls.set_default_values()
        if stream:
            cls.set_from_yaml(stream=stream)
        else:
            cls.set_from_yaml(stream=toggles.settings_file)
        if features:  # allow test injection
            for key in features.__dict__.keys():
                toggles.__dict__[key] = features.__dict__[key]
        for key in sorted(toggles.__dict__.keys()):
            value = toggles.__dict__.get(key)
            logging.debug("{0} = {1}".format(key, value))
        cls.set_aws_environment()

    @staticmethod
    def set_default_values():

        # identifier for this specific environment
        toggles.environment_identifier = "{}{}".format(
            os.environ.get('STACK_PREFIX', 'Spa'),
            os.environ.get('ENVIRONMENT', 'Alpha'))

        # use environment to locate settings file
        toggles.settings_file = os.environ.get('SETTINGS', 'settings.yaml')

        # other default values
        toggles.automation_cockpit_markdown_text = "# Sustainable Personal Accounts Dashboard\nCurrently under active development (alpha)"
        toggles.automation_role_name_to_manage_codebuild = 'AWSControlTowerExecution'
        toggles.automation_subscribed_email_addresses = []
        toggles.automation_tags = {}
        toggles.automation_verbosity = 'INFO'

    @classmethod
    def set_from_settings(cls, settings={}):
        for key in settings.keys():
            if type(settings[key]) == dict:
                for subkey in settings[key].keys():
                    flatten = "{0}_{1}".format(key, subkey)
                    value = settings[key].get(subkey)
                    cls.set_attribute(flatten, value)
            else:
                cls.set_attribute(key, settings[key])

    @classmethod
    def set_from_yaml(cls, stream):
        if type(stream) == str:
            with open(stream) as handle:
                logging.info(f"Loading configuration from '{stream}'")
                settings = yaml.safe_load(handle)
                cls.set_from_settings(settings)
        else:
            settings = yaml.safe_load(stream)
            cls.set_from_settings(settings)

    @classmethod
    def set_attribute(cls, key, value):
        cls.validate_attribute(key, value)
        if key == 'organizational_units':
            value = cls.transform_organizational_units(units=value)
        setattr(toggles, key, value)

    @classmethod
    def validate_attribute(cls, key, value):
        if kind := cls.ALLOWED_ATTRIBUTES.get(key):
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

    @staticmethod
    def transform_organizational_units(units):
        ''' make a dictionary out of a list of OU, using identifier as key '''
        transformed = {}
        for unit in units:
            key = unit['identifier']
            transformed[key] = {k: unit[k] for k in unit.keys() if k != 'identifier'}
        return transformed

    @staticmethod
    def set_aws_environment():
        account = os.environ.get('CDK_DEFAULT_ACCOUNT', None)
        if not account:  # fall back on current aws profile
            sts = boto3.client('sts')
            account = sts.get_caller_identity().get('Account')
        toggles.aws_account = account

        region = os.environ.get('CDK_DEFAULT_REGION', None)
        if not region:  # fall back on default region for current profile
            session = boto3.session.Session()
            region = session.region_name
        toggles.aws_region = region

        logging.debug("AWS environment is account '{0}' and region '{1}'".format(account, region))
        toggles.aws_environment = Environment(account=account, region=region)
