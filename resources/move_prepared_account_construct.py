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
from aws_cdk.aws_events import EventPattern, Rule
from aws_cdk.aws_events_targets import LambdaFunction
from aws_cdk.aws_lambda import Function


class MovePreparedAccount(Construct):

    def __init__(self, scope: Construct, id: str, parameters={}, permissions=[]) -> None:
        super().__init__(scope, id)
        self.functions = [
            self.on_codebuild(parameters=parameters, permissions=permissions),
            self.on_event(parameters=parameters, permissions=permissions)
        ]

    def on_codebuild(self, parameters, permissions) -> Function:
        function = Function(
            self, "OnCodebuild",
            function_name="{}MovePreparedAccountOnCodebuild".format(toggles.environment_identifier),
            description="Change state of prepared accounts to released",
            handler="move_prepared_account_handler.handle_codebuild_event",
            reserved_concurrent_executions=10,
            **parameters)

        for permission in permissions:
            function.add_to_role_policy(permission)

        Rule(self, "CodebuildRule",
             event_pattern=EventPattern(
                 source=['aws.codebuild'],
                 detail={"build-status": ["SUCCEEDED", "FAILED", "STOPPED"]},
                 detail_type=["CodeBuild Build State Change"]),
             targets=[LambdaFunction(function)])

        return function

    def on_event(self, parameters, permissions) -> Function:
        function = Function(
            self, "OnEvent",
            function_name="{}MovePreparedAccountOnEvent".format(toggles.environment_identifier),
            description="Change state of prepared accounts to released",
            handler="move_prepared_account_handler.handle_local_event",
            reserved_concurrent_executions=10,
            **parameters)

        for permission in permissions:
            function.add_to_role_policy(permission)

        Rule(self, "EventRule",
             event_pattern=EventPattern(
                 source=['SustainablePersonalAccounts'],
                 detail={"Environment": [toggles.environment_identifier]},
                 detail_type=['PreparedAccount']),
             targets=[LambdaFunction(function)])

        return function
