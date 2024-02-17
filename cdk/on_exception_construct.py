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
from aws_cdk.aws_iam import AnyPrincipal, Effect, ManagedPolicy, PolicyStatement
from aws_cdk.aws_lambda import Function, FunctionUrlAuthType
from aws_cdk.aws_sns import Topic
from aws_cdk.aws_sns_subscriptions import EmailSubscription
from aws_cdk.aws_ssmincidents import CfnResponsePlan

from cdk import LoggingFunction
from lambdas import Events
from .parameters_construct import Parameters


class OnException(Construct):

    TOPIC_DISPLAY_NAME = "Topic for alerts identified in managed accounts"

    def __init__(self, scope: Construct, id: str, parameters={}) -> None:
        super().__init__(scope, id)

        self.plan = CfnResponsePlan(self, "ResponsePlan",
                                    name="{}ResponsePlan".format(toggles.environment_identifier),
                                    incident_template=dict(impact=5, title='An exception detected by SPA'))

        self.web_endpoints = {}

        self.TOPIC_NAME = "{}Alerts".format(toggles.environment_identifier)

        self.topic = Topic(
            self, "Topic",
            display_name=self.TOPIC_DISPLAY_NAME,
            topic_name=self.TOPIC_NAME)

        statement = PolicyStatement(effect=Effect.ALLOW,
                                    actions=['sns:Publish'],
                                    conditions=dict(StringEquals={"aws:PrincipalOrgID": toggles.aws_organization_id}),
                                    principals=[AnyPrincipal()],
                                    resources=[self.topic.topic_arn])
        self.topic.add_to_resource_policy(statement)

        if toggles.features_with_email_subscriptions_on_alerts:
            for recipient in toggles.features_with_email_subscriptions_on_alerts:
                self.topic.add_subscription(EmailSubscription(recipient))

        parameters['environment']['RESPONSE_PLAN_ARN'] = self.plan.attr_arn
        parameters['environment']['REPORTING_EXCEPTIONS_PREFIX'] = toggles.reporting_exceptions_prefix
        parameters['environment']['WEB_ENDPOINTS_PARAMETER'] = Parameters.get_parameter(toggles.environment_identifier, Parameters.WEB_ENDPOINTS_PARAMETER)
        parameters['environment']['TOPIC_ARN'] = self.topic.topic_arn
        parameters['reserved_concurrent_executions'] = 1  # throttle above 10 RPS

        self.functions = [self.on_exception(parameters=parameters),
                          self.on_download(parameters=parameters)]

    def on_exception(self, parameters) -> Function:

        function = LoggingFunction(self,
                                   name="OnException",
                                   description="Handle exceptions",
                                   trigger="FromEvent",
                                   handler="on_exception_handler.handle_exception",
                                   parameters=parameters)

        function.role.add_managed_policy(ManagedPolicy.from_aws_managed_policy_name('AWSIncidentManagerResolverAccess'))
        function.add_to_role_policy(PolicyStatement(effect=Effect.ALLOW,
                                                    actions=['ssm-incidents:TagResource'],
                                                    resources=['*']))

        Rule(self, "EventRule",
             description="Route events from SPA to listening lambda function",
             event_pattern=EventPattern(
                 source=['SustainablePersonalAccounts'],
                 detail={"Environment": [toggles.environment_identifier]},
                 detail_type=Events.EXCEPTION_EVENT_LABELS),
             targets=[LambdaFunction(function)])

        return function

    def on_download(self, parameters) -> Function:

        function = LoggingFunction(self,
                                   name="OnExceptionAttachmentDownload",
                                   description="Serve requests for attachment download",
                                   trigger="FromUrl",
                                   handler="on_exception_handler.handle_attachment_request",
                                   parameters=parameters)

        self.web_endpoints["OnException.DownloadAttachment.WebEndpoint"] = function.add_function_url(auth_type=FunctionUrlAuthType.NONE,
                                                                                                     cors=dict(allowed_origins=["*"])).url

        return function
