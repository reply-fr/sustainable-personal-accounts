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

import boto3
import logging

from constructs import Construct
from aws_cdk import Duration
from aws_cdk.aws_events import EventPattern, Rule
from aws_cdk.aws_events_targets import LambdaFunction
from aws_cdk.aws_iam import AnyPrincipal, Effect, PolicyStatement, ServicePrincipal
from aws_cdk.aws_sqs import Queue
from aws_cdk.aws_sns import Topic
from aws_cdk.aws_sns_subscriptions import EmailSubscription
from aws_cdk.aws_lambda import Function
from aws_cdk.aws_lambda_event_sources import SqsEventSource

from lambdas import Worker


class OnAlert(Construct):

    QUEUE_NAME = "SpaAlerts"

    TOPIC_DISPLAY_NAME = "Topic for alerts identified in managed accounts"
    TOPIC_NAME = "SpaAlerts"

    def __init__(self, scope: Construct, id: str, parameters={}, permissions=[]) -> None:
        super().__init__(scope, id)

        self.topic = Topic(
            self, "Topic",
            display_name=self.TOPIC_DISPLAY_NAME,
            topic_name=self.TOPIC_NAME)

        statement = PolicyStatement(effect=Effect.ALLOW,
                                    actions=['sns:Publish'],
                                    conditions=dict(StringEquals={"aws:PrincipalOrgID": self.get_organization_identifier()}),
                                    principals=[AnyPrincipal()],
                                    resources=[self.topic.topic_arn])
        self.topic.add_to_resource_policy(statement)

        for recipient in toggles.features_with_email_subscriptions_on_alerts:
            self.topic.add_subscription(EmailSubscription(recipient))

        self.queue = Queue(self, "Queue", queue_name=self.QUEUE_NAME)

        statement = PolicyStatement(effect=Effect.ALLOW,
                                    actions=['sqs:SendMessage'],
                                    conditions=dict(StringEquals={"aws:PrincipalOrgID": self.get_organization_identifier()}),
                                    principals=[AnyPrincipal()],
                                    resources=[self.queue.queue_arn])
        self.queue.add_to_resource_policy(statement)

        statement = PolicyStatement(effect=Effect.ALLOW,
                                    actions=['sqs:SendMessage'],
                                    principals=[ServicePrincipal('sns.amazonaws.com')],
                                    resources=[self.queue.queue_arn])
        self.queue.add_to_resource_policy(statement)

        parameters['environment']['TOPIC_ARN'] = self.topic.topic_arn
        self.functions = [self.on_sqs(parameters=parameters, permissions=permissions, queue=self.queue),
                          self.on_codebuild(parameters=parameters, permissions=permissions)]

    def on_sqs(self, parameters, permissions, queue) -> Function:
        parameters['timeout'] = Duration.seconds(20)
        function = Function(
            self, "FromAlert",
            function_name="{}OnAlertFromSqs".format(toggles.environment_identifier),
            description="Be notified on an alert",
            handler="on_alert_handler.handle_sqs_event",
            **parameters)

        for permission in permissions:
            function.add_to_role_policy(permission)

        function.add_event_source(SqsEventSource(queue))

        return function

    def on_codebuild(self, parameters, permissions) -> Function:
        function = Function(
            self, "FromCodebuild",
            function_name="{}OnAlertFromCodebuild".format(toggles.environment_identifier),
            description="Be notified on a failed Codebuild project",
            handler="on_alert_handler.handle_codebuild_event",
            **parameters)

        for permission in permissions:
            function.add_to_role_policy(permission)

        Rule(self, "CodebuildRule",
             description="Route the failure of Codebuild project to lambda function",
             event_pattern=EventPattern(
                 source=['aws.codebuild'],
                 detail={"build-status": ["FAILED", "STOPPED"],
                         "project-name": [Worker.PROJECT_NAME_FOR_ACCOUNT_PREPARATION]},
                 detail_type=["CodeBuild Build State Change"]),
             targets=[LambdaFunction(function)])

        return function

    def get_organization_identifier(self):
        try:
            details = boto3.client('organizations').describe_organization()
            return details['Organization']['Id']
        except Exception as error:
            logging.exception(error)
            return 'o-is-unknown'
