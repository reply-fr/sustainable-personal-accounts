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

from constructs import Construct
from aws_cdk import Duration, Stack, Tags
from aws_cdk.aws_iam import Effect, PolicyStatement
from aws_cdk.aws_lambda import Architecture, AssetCode, Runtime, Tracing
from aws_cdk.aws_logs import RetentionDays

from .check_accounts_construct import CheckAccounts
from .cockpit_construct import Cockpit
from .on_alert_construct import OnAlert
from .on_assigned_account_construct import OnAssignedAccount
from .on_events_construct import OnEvents
from .on_expired_account_construct import OnExpiredAccount
from .on_maintenance_window_construct import OnMaintenanceWindow
from .on_prepared_account_construct import OnPreparedAccount
from .on_purged_account_construct import OnPurgedAccount
from .on_released_account_construct import OnReleasedAccount
from .on_vanilla_account_construct import OnVanillaAccount
from .parameters_construct import Parameters


class ServerlessStack(Stack):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, env=toggles.aws_environment, **kwargs)

        Parameters(self, "Parameters")

        # passed to all lambda functions
        environment = self.get_environment()
        parameters = self.get_parameters(environment=environment)
        permissions = self.get_permissions()

        labels = [
            'CheckAccounts',
            'OnAlert',
            'OnAssignedAccount',
            'OnEvents',
            'OnExpiredAccount',
            'OnMaintenanceWindow',
            'OnPreparedAccount',
            'OnPurgedAccount',
            'OnReleasedAccount',
            'OnVanillaAccount']

        monitored_functions = []
        for label in labels:
            construct = globals()[label](self, label, parameters=parameters.copy(), permissions=permissions.copy())
            monitored_functions.extend(construct.functions)

        Cockpit(self,
                "{}Cockpit".format(toggles.environment_identifier),
                functions=monitored_functions)

        for key in toggles.automation_tags.keys():  # cascaded to constructs and other resources
            Tags.of(self).add(key, toggles.automation_tags[key])

    def get_environment(self) -> dict:  # shared across all lambda functions
        environment = dict(
            AUTOMATION_ACCOUNT=toggles.automation_account_id,
            AUTOMATION_REGION=toggles.automation_region,
            ENVIRONMENT_IDENTIFIER=toggles.environment_identifier,
            EVENT_BUS_ARN=f"arn:aws:events:{toggles.automation_region}:{toggles.automation_account_id}:event-bus/default",
            ORGANIZATIONAL_UNITS_PARAMETER=toggles.environment_identifier + Parameters.ORGANIZATIONAL_UNITS_PARAMETER,
            PREPARATION_BUILDSPEC_PARAMETER=toggles.environment_identifier + Parameters.PREPARATION_BUILDSPEC_PARAMETER,
            PURGE_BUILDSPEC_PARAMETER=toggles.environment_identifier + Parameters.PURGE_BUILDSPEC_PARAMETER,
            ROLE_ARN_TO_MANAGE_ACCOUNTS=toggles.automation_role_arn_to_manage_accounts,
            ROLE_NAME_TO_MANAGE_CODEBUILD=toggles.automation_role_name_to_manage_codebuild,
            VERBOSITY=toggles.automation_verbosity)
        return environment

    def get_parameters(self, environment) -> dict:  # passed to every lambda functions
        parameters = dict(
            architecture=Architecture.ARM_64,
            code=AssetCode("code"),
            environment=environment,
            log_retention=RetentionDays.THREE_MONTHS,
            timeout=Duration.seconds(900),
            runtime=Runtime.PYTHON_3_9,
            tracing=Tracing.ACTIVE)
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
                            actions=['sns:Publish', 'sns:Subscribe'],
                            resources=['*']),

            PolicyStatement(effect=Effect.ALLOW,
                            actions=['sqs:ReceiveMessage'],
                            resources=['*']),

            PolicyStatement(effect=Effect.ALLOW,
                            actions=['ssm:GetParameter'],
                            resources=['*']),

            PolicyStatement(effect=Effect.ALLOW,
                            actions=['sts:AssumeRole'],
                            resources=['*'])

        ]
