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


class ToMicrosoftTeams(Construct):

    def __init__(self, scope: Construct, id: str, parameters={}) -> None:
        super().__init__(scope, id)
        if toggles.features_with_microsoft_webhook_on_alerts:
            parameters['environment']['MICROSOFT_WEBHOOK_ON_ALERTS'] = toggles.features_with_microsoft_webhook_on_alerts
        self.functions = [self.on_event(parameters=parameters)]

    def on_event(self, parameters) -> Function:

        function = LoggingFunction(self,
                                   name="ToMicrosoftTeams",
                                   description="Transmit information to Microsoft Teams",
                                   trigger="OnEvent",
                                   handler="to_microsoft_teams_handler.handle_spa_event",
                                   parameters=parameters)

        Rule(self, "EventRule",
             description="Route an event to Microsoft Teams",
             event_pattern=EventPattern(
                 source=['SustainablePersonalAccounts'],
                 detail={"Environment": [toggles.environment_identifier]},
                 detail_type=["MessageToMicrosoftTeams"]),
             targets=[LambdaFunction(function)])

        return function
