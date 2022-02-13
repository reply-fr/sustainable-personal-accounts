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
from aws_cdk.aws_events import EventPattern, Rule
from aws_cdk.aws_events_targets import LambdaFunction
from aws_cdk.aws_lambda import Function


class MoveVanillaAccount(Construct):

    def __init__(self, scope: Construct, id: str, parameters={}, statements=[]) -> None:
        super().__init__(scope, id)

        # First handler is for MoveAccount events generated during account creation, or afterwards
        #
        parameters['environment']['ORGANIZATIONAL_UNITS'] = json.dumps(toggles.organizational_units)
        self.function = Function(
            self, "OnMove",
            description="Move created accounts to assigned state",
            handler="move_vanilla_account_handler.handle_move_event",
            **parameters)

        for statement in statements:
            self.function.add_to_role_policy(statement)

        Rule(self, "MoveRule",
             event_pattern=EventPattern(
                 source=['aws.organizations'],
                 detail=dict(
                     eventName=['MoveAccount'],
                     requestParameters=dict(destinationParentId=toggles.organizational_units))),
             targets=[LambdaFunction(self.function)])

        # Second handler is for TagResource events generated manually on an account
        #
        self.function = Function(
            self, "OnTag",
            description="Move created accounts to assigned state",
            handler="move_vanilla_account_handler.handle_tag_event",
            **parameters)

        for statement in statements:
            self.function.add_to_role_policy(statement)

        Rule(self, "TagRule",
             event_pattern=EventPattern(
                 source=['aws.organizations'],
                 detail=dict(
                     errorCode=[{"exists": False}],
                     eventName=["TagResource"],
                     eventSource=["organizations.amazonaws.com"])),
             targets=[LambdaFunction(self.function)])
