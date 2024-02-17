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
from aws_cdk.aws_iam import AnyPrincipal, Effect, PolicyStatement, ServicePrincipal
from aws_cdk.aws_sqs import Queue
from aws_cdk.aws_lambda import Function
from aws_cdk.aws_lambda_event_sources import SqsEventSource

from cdk import LoggingFunction
from lambdas import Worker


class OnAlert(Construct):

    def __init__(self, scope: Construct, id: str, parameters={}) -> None:
        super().__init__(scope, id)

        self.QUEUE_NAME = "{}Alerts".format(toggles.environment_identifier)

        self.queue = Queue(self, "Queue", queue_name=self.QUEUE_NAME, visibility_timeout=Duration.seconds(900))

        statement = PolicyStatement(effect=Effect.ALLOW,
                                    actions=['sqs:SendMessage'],
                                    conditions=dict(StringEquals={"aws:PrincipalOrgID": toggles.aws_organization_id}),
                                    principals=[AnyPrincipal()],
                                    resources=[self.queue.queue_arn])
        self.queue.add_to_resource_policy(statement)

        statement = PolicyStatement(effect=Effect.ALLOW,
                                    actions=['sqs:SendMessage'],
                                    principals=[ServicePrincipal('sns.amazonaws.com')],
                                    resources=[self.queue.queue_arn])
        self.queue.add_to_resource_policy(statement)

        self.functions = [self.on_sqs(parameters=parameters, queue=self.queue),
                          self.on_codebuild(parameters=parameters)]

    def on_sqs(self, parameters, queue) -> Function:

        function = LoggingFunction(self,
                                   name="OnAlertFromSqs",
                                   description="Handle alerts received over SQS queue",
                                   trigger="FromAlert",
                                   handler="on_alert_handler.handle_sqs_event",
                                   parameters=parameters)

        function.add_event_source(SqsEventSource(queue))

        return function

    def on_codebuild(self, parameters) -> Function:

        function = LoggingFunction(self,
                                   name="OnAlertFromCodebuild",
                                   description="Handle failures of CodeBuild projects",
                                   trigger="FromCodebuild",
                                   handler="on_alert_handler.handle_codebuild_event",
                                   parameters=parameters)

        Rule(self, "CodebuildRule",
             description="Route the failure of Codebuild project to lambda function",
             event_pattern=EventPattern(
                 source=['aws.codebuild'],
                 detail={"build-status": ["FAILED", "STOPPED"],
                         "project-name": [Worker.PROJECT_NAME_FOR_ACCOUNT_PREPARATION]},
                 detail_type=["CodeBuild Build State Change"]),
             targets=[LambdaFunction(function)])

        return function
