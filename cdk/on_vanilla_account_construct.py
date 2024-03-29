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

from cdk import LoggingFunction


class OnVanillaAccount(Construct):

    def __init__(self, scope: Construct, id: str, parameters={}) -> None:
        super().__init__(scope, id)

        self.functions = [
            self.on_account(parameters=parameters),
            self.on_tag(parameters=parameters)
        ]

    def on_account(self, parameters={}) -> Function:

        function = LoggingFunction(self,
                                   name="OnVanillaAccount",
                                   description="Change state of created accounts to assigned",
                                   trigger="FromAccount",
                                   handler="on_vanilla_account_handler.handle_organization_event",
                                   parameters=parameters)

        Rule(self, "NewRule",
             description="Route the landing of an account in managed organizational units to lambda function",
             event_pattern=EventPattern(
                 source=['aws.organizations'],
                 detail=dict(
                     eventName=['CreateAccount', 'MoveAccount'])),
             targets=[LambdaFunction(function)])

        return function

    def on_tag(self, parameters={}) -> Function:

        function = LoggingFunction(self,
                                   name="OnVanillaAccountTag",
                                   description="Change state of created accounts to assigned",
                                   trigger="FromTag",
                                   handler="on_vanilla_account_handler.handle_tag_event",
                                   parameters=parameters)

        Rule(self, "TagRule",
             description="Route the tagging of vanilla accounts to lambda function",
             event_pattern=EventPattern(
                 source=['aws.organizations'],
                 detail=dict(
                     errorCode=[{"exists": False}],
                     eventName=["TagResource"],
                     eventSource=["organizations.amazonaws.com"],
                     requestParameters=dict(tags=dict(key=[toggles.state_tag], value=["vanilla"])))),
             targets=[LambdaFunction(function)])

        return function
