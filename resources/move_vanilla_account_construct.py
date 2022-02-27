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


class MoveVanillaAccount(Construct):

    def __init__(self, scope: Construct, id: str, parameters={}, permissions=[]) -> None:
        super().__init__(scope, id)

        self.functions = [
            self.build_on_move(parameters=parameters, permissions=permissions),
            self.build_on_tag(parameters=parameters, permissions=permissions)
        ]

    def build_on_move(self, parameters={}, permissions=[]) -> Function:
        """ for events generated by aws organizations on account creation or move """

        function = Function(
            self, "OnMove",
            description="Change state of created accounts to assigned",
            handler="move_vanilla_account_handler.handle_move_event",
            reserved_concurrent_executions=1,
            **parameters)

        for permission in permissions:
            function.add_to_role_policy(permission)

        Rule(self, "MoveRule",
             event_pattern=EventPattern(
                 source=['aws.organizations'],
                 detail=dict(
                     eventName=['MoveAccount'],
                     requestParameters=dict(destinationParentId=list(toggles.organizational_units.keys())))),
             targets=[LambdaFunction(function)])

        return function

    def build_on_tag(self, parameters={}, permissions=[]) -> Function:
        """ for events generated by account tagging """

        function = Function(
            self, "OnTag",
            description="Change state of created accounts to assigned",
            handler="move_vanilla_account_handler.handle_tag_event",
            reserved_concurrent_executions=1,
            **parameters)

        for permission in permissions:
            function.add_to_role_policy(permission)

        Rule(self, "TagRule",
             event_pattern=EventPattern(
                 source=['aws.organizations'],
                 detail=dict(
                     errorCode=[{"exists": False}],
                     eventName=["TagResource"],
                     eventSource=["organizations.amazonaws.com"])),
             targets=[LambdaFunction(function)])

        return function
