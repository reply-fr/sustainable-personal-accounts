#!/usr/bin/env python3
"""
Copyright Reply.com or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
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
    def initialize(cls, stream=None, dry_run=False, features: SimpleNamespace = None):
        builtins.toggles = SimpleNamespace(dry_run=dry_run)
        cls.set_default_values()
        if stream:
            cls.set_from_yaml(stream=stream)
        else:
            try:  # load settings silently if file exists
                cls.set_from_yaml(stream=toggles.settings_file)
            except FileNotFoundError:
                logging.debug("Could not load settings from file '{}'".format(toggles.settings_file))
        cls.set_from_environment()
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
        toggles.environment_identifier = "{}-{}".format(
            os.environ.get('STACK_PREFIX', 'spa'),
            os.environ.get('ENVIRONMENT', 'experimental'))

        # use environment to locate settings file
        toggles.settings_file = os.environ.get('SETTINGS', 'settings.yaml')

    @staticmethod
    def set_from_environment(environ=None, mapping=None):

        environ = os.environ if environ is None else environ  # allow test injection

        if mapping is None:  # allow test injection
            mapping = dict()

        for key in mapping.keys():  # we only accept mapped environment variables
            value = environ.get(mapping[key])
            if value is not None:  # override only if environment variable has been set
                setattr(toggles, key, value)

    @staticmethod
    def set_from_settings(settings={}):
        for key in settings.keys():
            if type(settings[key]) == dict:
                for subkey in settings[key].keys():
                    flatten = "{0}_{1}".format(key, subkey)
                    value = settings[key].get(subkey)
                    setattr(toggles, flatten, value)
            else:
                setattr(toggles, key, settings[key])

    @classmethod
    def set_from_yaml(cls, stream):
        if type(stream) == str:
            with open(stream) as handle:
                logging.info("Loading configuration from '{}'".format(stream))
                settings = yaml.safe_load(handle)
                cls.set_from_settings(settings)
        else:
            settings = yaml.safe_load(stream)
            cls.set_from_settings(settings)

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
