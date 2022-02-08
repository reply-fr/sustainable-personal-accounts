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
from aws_cdk import Duration
from aws_cdk.aws_events import EventPattern, Rule
from aws_cdk.aws_events_targets import LambdaFunction
from aws_cdk.aws_lambda import AssetCode, Function, Runtime
from aws_cdk.aws_logs import RetentionDays


class SignalAssignedAccountConstruct(Construct):

    def __init__(self, scope: Construct, id: str) -> None:
        super().__init__(scope, id)

        lambdaFn = Function(
            self, "signal-assigned-account",
            code=AssetCode("code"),
            description="Start preparation of an assigned account",
            handler="signal_assigned_account_handler.handler",
            environment=dict(ASSIGNED_ACCOUNTS_ORGANIZATIONAL_UNIT=toggles.assigned_accounts_organizational_unit),
            log_retention=RetentionDays.THREE_MONTHS,
            timeout=Duration.seconds(900),
            runtime=Runtime.PYTHON_3_9)

        rule = Rule(
            self, "Rule",
            event_pattern=EventPattern(
                source=['aws.organization'],
                detail=dict(
                    eventName=['MoveAccount'],
                    requestParameters=dict(destinationParentId=[toggles.assigned_accounts_organizational_unit]))),
            targets=[LambdaFunction(lambdaFn)])