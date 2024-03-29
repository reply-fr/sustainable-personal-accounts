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
from aws_cdk.aws_events import EventPattern, Rule, RuleTargetInput
from aws_cdk.aws_events_targets import SqsQueue
from aws_cdk.aws_lambda import Function
from aws_cdk.aws_lambda_event_sources import SqsEventSource
from aws_cdk.aws_sqs import Queue

from cdk import LoggingFunction
from .parameters_construct import Parameters


class OnAssignedAccount(Construct):

    def __init__(self, scope: Construct, id: str, parameters={}) -> None:
        super().__init__(scope, id)

        self.queue = Queue(self, "Queue", visibility_timeout=Duration.minutes(15))

        parameters['environment']['PREPARATION_BUILDSPEC_PARAMETER'] = Parameters.get_parameter(toggles.environment_identifier, Parameters.PREPARATION_BUILDSPEC_PARAMETER)
        self.functions = [self.on_tag(parameters=parameters, queue=self.queue)]

    def on_tag(self, parameters, queue) -> Function:

        Rule(self, "TagRule",
             description="Route the tagging of assigned accounts to queue",
             event_pattern=EventPattern(
                 source=['aws.organizations'],
                 detail=dict(
                     errorCode=[{"exists": False}],
                     eventName=["TagResource"],
                     eventSource=["organizations.amazonaws.com"],
                     requestParameters=dict(tags=dict(key=[toggles.state_tag], value=["assigned"])))),
             targets=[SqsQueue(queue=queue, message=RuleTargetInput.from_event_path('$.detail'))])

        function = LoggingFunction(self,
                                   name="OnAssignedAccountFromQueue",
                                   description="Start preparation of an assigned account",
                                   trigger="FromQueue",
                                   handler="on_assigned_account_handler.handle_tag_event",
                                   parameters=parameters)

        queue.grant_consume_messages(function)
        function.add_event_source(SqsEventSource(queue, batch_size=1, max_concurrency=10))

        return function
