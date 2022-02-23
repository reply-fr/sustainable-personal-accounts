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

from constructs import Construct
from aws_cdk import Duration, Stack
from aws_cdk.aws_iam import Effect, PolicyStatement
from aws_cdk.aws_lambda import AssetCode, Runtime
from aws_cdk.aws_logs import RetentionDays

from .cockpit_construct import Cockpit
from .listen_events_construct import ListenEvents
from .move_expired_accounts_construct import MoveExpiredAccounts
from .move_prepared_account_construct import MovePreparedAccount
from .move_purged_account_construct import MovePurgedAccount
from .move_vanilla_account_construct import MoveVanillaAccount
from .parameters_construct import Parameters
from .signal_assigned_account_construct import SignalAssignedAccount
from .signal_expired_account_construct import SignalExpiredAccount


class ServerlessStack(Stack):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, env=toggles.aws_environment, **kwargs)

        Parameters(self, "{}Parameters".format(toggles.environment_identifier))

        # passed to all lambda functions
        environment = self.get_environment()
        parameters = self.get_parameters(environment=environment)
        permissions = self.get_permissions()

        constructs = [
            ListenEvents(self, "ListenEvents", parameters=parameters, permissions=permissions),
            SignalAssignedAccount(self, "SignalAssignedAccount", parameters=parameters, permissions=permissions),
            MovePreparedAccount(self, "MovePreparedAccount", parameters=parameters, permissions=permissions),
            MoveExpiredAccounts(self, "MoveExpiredAccounts", parameters=parameters, permissions=permissions),
            MoveVanillaAccount(self, "MoveVanillaAccount", parameters=parameters, permissions=permissions),
            SignalExpiredAccount(self, "SignalExpiredAccount", parameters=parameters, permissions=permissions),
            MovePurgedAccount(self, "MovePurgedAccount", parameters=parameters, permissions=permissions)
        ]
        functions = []
        for construct in constructs:
            functions.extend(construct.functions)

        Cockpit(self,
                "{}Cockpit".format(toggles.environment_identifier),
                functions=functions)

    def get_environment(self) -> dict:  # shared across all lambda functions
        environment = dict(
            ORGANIZATIONAL_UNITS_PARAMETER=Parameters.ORGANIZATIONAL_UNITS_PARAMETER,
            PREPARATION_BUILDSPEC_PARAMETER=Parameters.PREPARATION_BUILDSPEC_PARAMETER,
            PURGE_BUILDSPEC_PARAMETER=Parameters.PURGE_BUILDSPEC_PARAMETER,
            DRY_RUN="TRUE" if toggles.dry_run else "FALSE",
            EVENT_BUS_ARN=toggles.event_bus_arn,
            ROLE_ARN_TO_MANAGE_ACCOUNTS=toggles.role_arn_to_manage_accounts)
        if toggles.role_arn_to_put_events:
            environment['ROLE_ARN_TO_PUT_EVENTS'] = toggles.role_arn_to_put_events
        if toggles.role_name_to_manage_codebuild:
            environment['ROLE_NAME_TO_MANAGE_CODEBUILD'] = toggles.role_name_to_manage_codebuild
        return environment

    def get_parameters(self, environment) -> dict:  # used to build lambda functions
        parameters = dict(
            code=AssetCode("code"),
            environment=environment,
            log_retention=RetentionDays.THREE_MONTHS,
            reserved_concurrent_executions=toggles.maximum_concurrent_executions,
            timeout=Duration.seconds(900),
            runtime=Runtime.PYTHON_3_9)
        return parameters

    def get_permissions(self) -> list:  # given to all lambda functions
        return [

            PolicyStatement(effect=Effect.ALLOW,
                            actions=['cloudwatch:PutMetricData'],
                            resources=['*']),

            PolicyStatement(effect=Effect.ALLOW,
                            actions=['events:PutEvents'],
                            resources=['*']),

            PolicyStatement(effect=Effect.ALLOW,
                            actions=['organizations:TagResource'],
                            resources=['*']),

            PolicyStatement(effect=Effect.ALLOW,
                            actions=['ssm:GetParameter'],
                            resources=['*']),

            PolicyStatement(effect=Effect.ALLOW,
                            actions=['sts:AssumeRole'],
                            resources=['*'])

        ]
