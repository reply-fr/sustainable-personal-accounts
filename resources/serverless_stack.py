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
from aws_cdk import Duration, Stack
from aws_cdk.aws_iam import Effect, PolicyStatement
from aws_cdk.aws_lambda import AssetCode, Runtime
from aws_cdk.aws_logs import RetentionDays

from .cockpit_construct import Cockpit
from .listen_account_events_construct import ListenAccountEvents
from .move_expired_accounts_construct import MoveExpiredAccounts
from .move_prepared_account_construct import MovePreparedAccount
from .move_purged_account_construct import MovePurgedAccount
from .move_vanilla_account_construct import MoveVanillaAccount
from .signal_assigned_account_construct import SignalAssignedAccount
from .signal_expired_account_construct import SignalExpiredAccount


class ServerlessStack(Stack):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, env=toggles.aws_environment, **kwargs)

        parameters = dict(  # passed to all functions
            code=AssetCode("code"),
            environment=dict(
                ROLE_TO_MANAGE_ACCOUNTS=toggles.role_to_manage_accounts,
                ROLE_TO_PUT_EVENTS=toggles.role_to_put_events),
            log_retention=RetentionDays.THREE_MONTHS,
            reserved_concurrent_executions=toggles.maximum_concurrent_executions,
            timeout=Duration.seconds(900),
            runtime=Runtime.PYTHON_3_9)

        statements = [  # permissions given to all functions

            PolicyStatement(effect=Effect.ALLOW,
                            actions=['cloudwatch:PutMetricData'],
                            resources=['*']),

            PolicyStatement(effect=Effect.ALLOW,
                            actions=['events:PutEvents'],
                            resources=['*']),

            PolicyStatement(effect=Effect.ALLOW,
                            actions=['organizations:TagResource'],
                            resources=['*'])

        ]

        functions = [
            ListenAccountEvents(self, "ListenAccountEvents", parameters=parameters, statements=statements),
            MoveVanillaAccount(self, "MoveVanillaAccount", parameters=parameters, statements=statements),
            SignalAssignedAccount(self, "SignalAssignedAccount", parameters=parameters, statements=statements),
            MovePreparedAccount(self, "MovePreparedAccount", parameters=parameters, statements=statements),
            MoveExpiredAccounts(self, "MoveExpiredAccounts", parameters=parameters, statements=statements),
            SignalExpiredAccount(self, "SignalExpiredAccount", parameters=parameters, statements=statements),
            MovePurgedAccount(self, "MovePurgedAccount", parameters=parameters, statements=statements)
        ]

        Cockpit(self,
                "{}Cockpit".format(toggles.environment_identifier),
                functions=[x.function for x in functions])
