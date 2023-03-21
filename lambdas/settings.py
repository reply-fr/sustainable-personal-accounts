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

import json

from boto3.session import Session
import botocore

from . import Account


class Settings:

    PARAMETER_SEPARATOR = "/"  # /!\ to be duplicated in resources/parameters_construct.py
    ACCOUNTS_PARAMETER = "Accounts"
    ORGANIZATIONAL_UNITS_PARAMETER = "OrganizationalUnits"

    @classmethod
    def enumerate_accounts(cls, environment, session=None):
        path = cls.get_account_parameter_name(environment=environment)
        return cls.enumerate_identifiers_by_path(path=path, session=session)

    @classmethod
    def enumerate_organizational_units(cls, environment, session=None):
        path = cls.get_organizational_unit_parameter_name(environment=environment)
        return cls.enumerate_identifiers_by_path(path=path, session=session)

    @classmethod
    def get_account_parameter_name(cls, environment, identifier=None):
        attributes = ['', environment, cls.ACCOUNTS_PARAMETER]
        if identifier:
            attributes.append(identifier)
        return cls.PARAMETER_SEPARATOR.join(attributes)

    @classmethod
    def get_organizational_unit_parameter_name(cls, environment, identifier=None):
        attributes = ['', environment, cls.ORGANIZATIONAL_UNITS_PARAMETER]
        if identifier:
            attributes.append(identifier)
        return cls.PARAMETER_SEPARATOR.join(attributes)

    @classmethod
    def enumerate_identifiers_by_path(cls, path, session=None):
        session = session or Session()
        chunk = session.client('ssm').get_parameters_by_path(Path=path)
        while chunk.get('Parameters'):
            for item in chunk.get('Parameters'):
                attributes = json.loads(item['Value'])
                yield attributes['identifier']
            more = chunk.get('NextToken')
            if more:
                chunk = session.client('ssm').get_parameters_by_path(Path=path, NextToken=more)
            else:
                break

    @classmethod
    def get_account_settings(cls, environment, identifier, session=None) -> dict:
        session = session or Session()
        name = cls.get_account_parameter_name(environment=environment, identifier=identifier)
        item = session.client('ssm').get_parameter(Name=name)
        if item:
            return json.loads(item['Parameter']['Value'])

    @classmethod
    def get_organizational_unit_settings(cls, environment, identifier, session=None) -> dict:
        session = session or Session()
        name = cls.get_organizational_unit_parameter_name(environment=environment, identifier=identifier)
        item = session.client('ssm').get_parameter(Name=name)
        return json.loads(item['Parameter']['Value'])

    @classmethod
    def get_settings_for_account(cls, environment, identifier, session=None) -> dict:
        '''return either explicit account settings, or settings of parent organizational unit'''
        try:
            settings = cls.get_account_settings(environment=environment, identifier=identifier, session=session)
        except botocore.exceptions.ClientError:
            details = Account.describe(id=identifier, session=session)
            try:
                settings = cls.get_organizational_unit_settings(environment=environment, identifier=details.unit, session=session)
            except botocore.exceptions.ClientError:
                raise ValueError(f"No settings could be found for account {identifier}")
        return settings
