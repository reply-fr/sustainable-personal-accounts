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

    ORGANIZATIONAL_UNITS_PARAMETER = "OrganizationalUnits"
    PREPARATION_BUILDSPEC_PARAMETER = "PreparationBuildspecTemplate"
    PURGE_BUILDSPEC_PARAMETER = "PurgeBuildspecTemplate"

    def __init__(self, scope: Construct, id: str) -> None:
        super().__init__(scope, id)

        StringParameter(
            self, "OrganisationalUnits",
            string_value=json.dumps(toggles.organizational_units, indent=4),
            data_type=ParameterDataType.TEXT,
            description="Parameters for managed organizational units",
            parameter_name=toggles.environment_identifier + self.ORGANIZATIONAL_UNITS_PARAMETER,
            tier=ParameterTier.STANDARD)

        StringParameter(
            self, "PreparationTemplate",
            string_value=self.get_buildspec_for_preparation(),
            data_type=ParameterDataType.TEXT,
            description="Buildspec template used for account preparation",
            parameter_name=toggles.environment_identifier + self.PREPARATION_BUILDSPEC_PARAMETER,
            tier=ParameterTier.STANDARD)

        StringParameter(
            self, "PurgeTemplate",
            string_value=self.get_buildspec_for_purge(),
            data_type=ParameterDataType.TEXT,
            description="Buildspec template used for the purge of accounts",
            parameter_name=toggles.environment_identifier + self.PURGE_BUILDSPEC_PARAMETER,
            tier=ParameterTier.ADVANCED)  # up to 8k template

    def get_buildspec_for_preparation(self):
        logging.debug("Getting buildspec for account preparation")
        with open(toggles.worker_preparation_buildspec_template_file) as stream:
            return stream.read()

    def get_buildspec_for_purge(self):
        logging.debug("Getting buildspec for the purge of accounts")
        with open(toggles.worker_purge_buildspec_template_file) as stream:
            return stream.read()
