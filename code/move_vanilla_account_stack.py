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
from aws_cdk.aws_events import EventPattern, Rule
from aws_cdk.aws_events_targets import LambdaFunction
from aws_cdk.aws_lambda import AssetCode, Function, Runtime


class MoveVanillaAccountStack(Stack):

    def __init__(self, scope: Construct, id: str) -> None:
        super().__init__(scope, id)

        lambdaFn = Function(
            self, "move-vanilla-account",
            code=AssetCode("code"),
            handler="move_vanilla_account_handler.handler",
            environment=dict(VANILLA_ACCOUNTS_OU='1234',
                             ASSIGNED_ACCOUNTS_OU='5678'),
            timeout=Duration.seconds(900),
            runtime=Runtime.PYTHON_3_9)

        rule = Rule(
            self, "Rule",
            event_pattern=EventPattern(
                source=['aws.organization'],
                detail_type=['AWS API Call via CloudTrail'],
                detail=dict(
                    eventName=['MoveAccount'],
                    requestParameters=dict(destinationParentId=['ou-2pcw-56n2rgox']))),
            targets=[LambdaFunction(lambdaFn)])
