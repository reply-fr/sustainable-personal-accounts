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
import logging

from constructs import Construct
from aws_cdk.aws_ssm import ParameterDataType, ParameterTier, StringParameter


class Parameters(Construct):

    PARAMETER_SEPARATOR = "/"  # /!\ to be duplicated in code/settings.py
    ACCOUNTS_PARAMETER = "Accounts"
    DOCUMENTS_PARAMETER = "Documents"
    ORGANIZATIONAL_UNITS_PARAMETER = "OrganizationalUnits"
    PREPARATION_BUILDSPEC_PARAMETER = "PreparationBuildspecTemplate"
    PURGE_BUILDSPEC_PARAMETER = "PurgeBuildspecTemplate"
    WEB_ENDPOINTS_PARAMETER = "WebEndpoints"

    def __init__(self, scope: Construct, id: str, web_endpoints={}) -> None:
        super().__init__(scope, id)

        for identifier in toggles.accounts.keys():  # one parameter per managed account
            StringParameter(
                self, f"a-{identifier}",
                string_value=json.dumps(toggles.accounts[identifier], indent=4),
                data_type=ParameterDataType.TEXT,
                description="Parameters for managed account {}".format(identifier),
                parameter_name=self.get_account_parameter(environment=toggles.environment_identifier,
                                                          identifier=identifier),
                tier=ParameterTier.STANDARD)

        for identifier in toggles.organizational_units.keys():  # one parameter per managed organizational unit
            StringParameter(
                self, identifier,
                string_value=json.dumps(toggles.organizational_units[identifier], indent=4),
                data_type=ParameterDataType.TEXT,
                description="Parameters for managed organizational unit {}".format(identifier),
                parameter_name=self.get_organizational_unit_parameter(environment=toggles.environment_identifier,
                                                                      identifier=identifier),
                tier=ParameterTier.STANDARD)

        string_value = self.get_buildspec_for_preparation()  # the buildspec for account preparation
        StringParameter(
            self, "PreparationTemplate",
            string_value=string_value,
            data_type=ParameterDataType.TEXT,
            description="Buildspec template used for account preparation",
            parameter_name=self.get_parameter(toggles.environment_identifier, self.PREPARATION_BUILDSPEC_PARAMETER),
            tier=ParameterTier.ADVANCED)

        string_value = self.get_buildspec_for_purge()  # the buildspec for account purge
        StringParameter(
            self, "PurgeTemplate",
            string_value=string_value,
            data_type=ParameterDataType.TEXT,
            description="Buildspec template used for the purge of accounts",
            parameter_name=self.get_parameter(toggles.environment_identifier, self.PURGE_BUILDSPEC_PARAMETER),
            tier=ParameterTier.STANDARD if len(string_value) < 4096 else ParameterTier.ADVANCED)

        StringParameter(
            self, "WebEndpoints",
            string_value=json.dumps(web_endpoints, indent=4),
            data_type=ParameterDataType.TEXT,
            description="The map of web endpoints exposed to the Internet",
            parameter_name=self.get_parameter(toggles.environment_identifier, self.WEB_ENDPOINTS_PARAMETER),
            tier=ParameterTier.STANDARD if len(string_value) < 4096 else ParameterTier.ADVANCED)

        if toggles.features_with_end_user_documents:
            for label, file in toggles.features_with_end_user_documents.items():
                content = self.get_document(label, file)
                StringParameter(
                    self, label,
                    string_value=content,
                    data_type=ParameterDataType.TEXT,
                    description=f"Document {label}",
                    parameter_name=self.get_document_parameter(environment=toggles.environment_identifier,
                                                               identifier=label),
                    tier=ParameterTier.STANDARD if len(string_value) < 4096 else ParameterTier.ADVANCED)

    @classmethod
    def get_account_parameter(cls, environment, identifier=None):
        attributes = ['', environment, cls.ACCOUNTS_PARAMETER]
        if identifier:
            attributes.append(identifier)
        return cls.PARAMETER_SEPARATOR.join(attributes)

    @classmethod
    def get_document_parameter(cls, environment, identifier=None):
        attributes = ['', environment, cls.DOCUMENTS_PARAMETER]
        if identifier:
            attributes.append(identifier)
        return cls.PARAMETER_SEPARATOR.join(attributes)

    @classmethod
    def get_organizational_unit_parameter(cls, environment, identifier=None):
        attributes = ['', environment, cls.ORGANIZATIONAL_UNITS_PARAMETER]
        if identifier:
            attributes.append(identifier)
        return cls.PARAMETER_SEPARATOR.join(attributes)

    @classmethod
    def get_parameter(cls, environment, parameter):
        attributes = ['', environment, parameter]
        return cls.PARAMETER_SEPARATOR.join(attributes)

    def get_buildspec_for_preparation(self):
        logging.debug("Getting buildspec for the preparation of accounts")
        with open(toggles.worker_preparation_buildspec_template_file) as stream:
            return stream.read()

    def get_buildspec_for_purge(self):
        logging.debug("Getting buildspec for the purge of accounts")
        with open(toggles.worker_purge_buildspec_template_file) as stream:
            return stream.read()

    def get_document(self, label, file):
        logging.debug(f"Loading document {label} from file {file}")
        with open(file) as stream:
            return stream.read()
