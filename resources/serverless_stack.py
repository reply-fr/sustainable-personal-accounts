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
from .metering_construct import Metering
from .on_account_event_construct import OnAccountEvent
from .on_account_event_then_meter_construct import OnAccountEventThenMeter
from .on_alert_construct import OnAlert
from .on_assigned_account_construct import OnAssignedAccount
from .on_expired_account_construct import OnExpiredAccount
from .on_maintenance_window_construct import OnMaintenanceWindow
from .on_prepared_account_construct import OnPreparedAccount
from .on_purged_account_construct import OnPurgedAccount
from .on_released_account_construct import OnReleasedAccount
from .on_vanilla_account_construct import OnVanillaAccount
from .parameters_construct import Parameters
from .release_accounts_construct import ReleaseAccounts
from .reset_accounts_construct import ResetAccounts
from .to_microsoft_teams_construct import ToMicrosoftTeams


class ServerlessStack(Stack):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, env=toggles.aws_environment, **kwargs)

        Parameters(self, "Parameters")

        # lambda functions
        labels = [
            'CheckAccounts',
            'OnAccountEvent',
            'OnAccountEventThenMeter',
            'OnAlert',
            'OnAssignedAccount',
            'OnExpiredAccount',
            'OnMaintenanceWindow',
            'OnPreparedAccount',
            'OnPurgedAccount',
            'OnReleasedAccount',
            'OnVanillaAccount',
            'ReleaseAccounts',
            'ResetAccounts',
            'ToMicrosoftTeams']

        constructs = {}
        monitored_functions = []
        for label in labels:

            environment = self.get_environment().copy()
            parameters = self.get_parameters(environment=environment).copy()
            permissions = self.get_permissions().copy()

            construct = globals()[label](self, label, parameters=parameters, permissions=permissions)
            constructs[label] = construct
            monitored_functions.extend(construct.functions)

        Cockpit(self,
                "{}Cockpit-{}".format(toggles.environment_identifier, toggles.automation_region),
                functions=monitored_functions)

        Metering(self, "Metering", writers=constructs['OnAccountEventThenMeter'].functions)

        for key in toggles.automation_tags.keys():  # cascaded to constructs and other resources
            Tags.of(self).add(key, toggles.automation_tags[key])

    def get_environment(self) -> dict:  # shared across all lambda functions
        environment = dict(
            ACCOUNTS_PARAMETER=Parameters.get_account_parameter(environment=toggles.environment_identifier),
            AUTOMATION_ACCOUNT=toggles.automation_account_id,
            AUTOMATION_REGION=toggles.automation_region,
            ENVIRONMENT_IDENTIFIER=toggles.environment_identifier,
            EVENT_BUS_ARN=f"arn:aws:events:{toggles.automation_region}:{toggles.automation_account_id}:event-bus/default",
            ORGANIZATIONAL_UNITS_PARAMETER=Parameters.get_organizational_unit_parameter(environment=toggles.environment_identifier),
            PREPARATION_BUILDSPEC_PARAMETER=toggles.environment_identifier + Parameters.PREPARATION_BUILDSPEC_PARAMETER,
            PURGE_BUILDSPEC_PARAMETER=toggles.environment_identifier + Parameters.PURGE_BUILDSPEC_PARAMETER,
            ROLE_ARN_TO_MANAGE_ACCOUNTS=toggles.automation_role_arn_to_manage_accounts,
            ROLE_NAME_TO_MANAGE_CODEBUILD=toggles.automation_role_name_to_manage_codebuild,
            TAG_PREFIX=toggles.features_with_tag_prefix,
            VERBOSITY=toggles.automation_verbosity)
        return environment

    def get_parameters(self, environment) -> dict:  # passed to every lambda functions
        parameters = dict(
            architecture=Architecture.ARM_64 if toggles.features_with_arm_architecture else Architecture.X86_64,
            code=AssetCode("lambda.out"),  # code and dependencies are copied there in Makefile
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
                            actions=['ssm:GetParameter', 'ssm:GetParameters', 'ssm:GetParametersByPath'],
                            resources=['*']),

            PolicyStatement(effect=Effect.ALLOW,
                            actions=['sts:AssumeRole'],
                            resources=['*'])

        ]
