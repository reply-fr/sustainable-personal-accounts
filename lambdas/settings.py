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

from boto3.session import Session
import botocore
from itertools import chain
import json
import logging
import os

from account import Account


class Settings:

    PARAMETER_SEPARATOR = "/"  # /!\ to be duplicated in resources/parameters_construct.py
    ACCOUNTS_PARAMETER = "Accounts"
    ORGANIZATIONAL_UNITS_PARAMETER = "OrganizationalUnits"

    cache = {}

    @classmethod
    def enumerate_all_managed_accounts(cls, session=None):
        listed_accounts = cls.list_managed_accounts(session=session)
        contained_accounts = cls.enumerate_accounts_in_managed_organizational_units(skip=listed_accounts, session=session)
        return chain(iter(listed_accounts), contained_accounts)

    @classmethod
    def list_managed_accounts(cls, session=None):
        logging.info("Listing configured accounts")
        return [id for id in cls.enumerate_accounts(session=session)]

    @classmethod
    def enumerate_accounts_in_managed_organizational_units(cls, skip=[], session=None):
        logging.info("Enumerating accounts in configured organizational units")
        for identifier in cls.enumerate_organizational_units(session=session):
            logging.info(f"Scanning organizational unit '{identifier}'")
            for account in Account.list(parent=identifier, skip=skip, session=session):
                yield account

    @classmethod
    def enumerate_accounts(cls, session=None):
        path = cls.get_account_parameter_name()
        return cls.enumerate_identifiers_by_path(path=path, session=session)

    @classmethod
    def enumerate_organizational_units(cls, session=None):
        path = cls.get_organizational_unit_parameter_name()
        return cls.enumerate_identifiers_by_path(path=path, session=session)

    @classmethod
    def enumerate_identifiers_by_path(cls, path, session=None):
        logging.debug(f"Enurating identifiers in path {path}")
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
    def get_account_parameter_name(cls, identifier=None):
        attributes = ['', cls.get_environment(), cls.ACCOUNTS_PARAMETER]
        if identifier:
            attributes.append(identifier)
        return cls.PARAMETER_SEPARATOR.join(attributes)

    @classmethod
    def get_account_settings(cls, identifier, session=None) -> dict:
        session = session or Session()
        name = cls.get_account_parameter_name(identifier=identifier)
        item = session.client('ssm').get_parameter(Name=name)
        if item:
            return json.loads(item['Parameter']['Value'])

    @classmethod
    def get_organizational_unit_parameter_name(cls, identifier=None):
        tokens = ['', cls.get_environment(), cls.ORGANIZATIONAL_UNITS_PARAMETER]
        if identifier:
            tokens.append(identifier)
        return cls.PARAMETER_SEPARATOR.join(tokens)

    @classmethod
    def get_organizational_unit_settings(cls, identifier, session=None) -> dict:
        if identifier in cls.cache.keys():
            return cls.cache[identifier]
        session = session or Session()
        name = cls.get_organizational_unit_parameter_name(identifier=identifier)
        item = session.client('ssm').get_parameter(Name=name)
        settings = json.loads(item['Parameter']['Value'])
        cls.cache[identifier] = settings
        return settings

    @classmethod
    def get_settings_for_account(cls, identifier, session=None) -> dict:
        '''return either explicit account settings, or settings inherited from parent organizational unit'''
        try:
            settings = cls.get_account_settings(identifier=identifier, session=session)
        except botocore.exceptions.ClientError as exception:
            try:
                unit = Account.get_organizational_unit(account=identifier)
                settings = cls.get_organizational_unit_settings(identifier=unit, session=session)
            except botocore.exceptions.ClientError:
                raise ValueError(f"No settings could be found for account {identifier}")
        return settings

    @classmethod
    def scan_settings_for_all_managed_accounts(cls):
        logging.debug("Scan settings for all managed accounts")
        accounts = {}
        for account in cls.enumerate_all_managed_accounts():
            logging.debug(f"Sannning account {account}")
            try:
                accounts[account] = Account.describe(account).__dict__
            except botocore.exceptions.ClientError:
                logging.error(f"No settings could be found for account {account}")
        return accounts

    @classmethod
    def get_environment(cls):
        return os.environ.get('ENVIRONMENT_IDENTIFIER', 'Spa')
