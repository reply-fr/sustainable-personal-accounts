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
from .parameters_construct import Parameters


class OnExpiredAccount(Construct):

    def __init__(self, scope: Construct, id: str, parameters={}) -> None:
        super().__init__(scope, id)

        parameters['environment']['PURGE_BUILDSPEC_PARAMETER'] = Parameters.get_parameter(toggles.environment_identifier, Parameters.PURGE_BUILDSPEC_PARAMETER)
        self.functions = [self.build_on_tag(parameters=parameters)]

    def build_on_tag(self, parameters) -> Function:

        function = LoggingFunction(self,
                                   name="OnExpiredAccount",
                                   description="Start the purge of an expired account",
                                   trigger="FromTag",
                                   handler="on_expired_account_handler.handle_tag_event",
                                   parameters=parameters)

        Rule(self, "TagRule",
             description="Route the tagging of expired accounts to lambda function",
             event_pattern=EventPattern(
                 source=['aws.organizations'],
                 detail=dict(
                     errorCode=[{"exists": False}],
                     eventName=["TagResource"],
                     eventSource=["organizations.amazonaws.com"],
                     requestParameters=dict(tags=dict(key=[toggles.state_tag], value=["expired"])))),
             targets=[LambdaFunction(function)])

        return function
