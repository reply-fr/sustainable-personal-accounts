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
from aws_cdk import RemovalPolicy
from aws_cdk.aws_dynamodb import AttributeType, BillingMode, Table, TableEncryption
from aws_cdk.aws_events import EventPattern, Rule, Schedule
from aws_cdk.aws_events_targets import LambdaFunction
from aws_cdk.aws_lambda import Function
from aws_cdk.aws_logs import LogGroup, RetentionDays

from lambdas import Events


class OnActivity(Construct):

    def __init__(self, scope: Construct, id: str, parameters={}) -> None:
        super().__init__(scope, id)

        self.table_name = toggles.environment_identifier + toggles.metering_activities_datastore
        self.table = Table(
            self, "ActivitiesTable",
            table_name=self.table_name,
            partition_key={'name': 'Identifier', 'type': AttributeType.STRING},
            sort_key={'name': 'Order', 'type': AttributeType.STRING},
            billing_mode=BillingMode.PAY_PER_REQUEST,
            encryption=TableEncryption.AWS_MANAGED,
            removal_policy=RemovalPolicy.DESTROY,
            time_to_live_attribute="Expiration")

        parameters['environment']['METERING_ACTIVITIES_DATASTORE'] = self.table_name
        parameters['environment']['METERING_ACTIVITIES_TTL'] = str(toggles.metering_activities_ttl_in_seconds)
        parameters['environment']['REPORTING_ACTIVITIES_PREFIX'] = toggles.reporting_activities_prefix
        self.functions = [self.on_event(parameters=parameters),
                          self.monthly(parameters=parameters),
                          self.daily(parameters=parameters)]

        for function in self.functions:
            self.table.grant_read_write_data(grantee=function)

    def on_event(self, parameters) -> Function:

        function_name = toggles.environment_identifier + "OnActivityEvent"

        LogGroup(self, function_name + "Log",
                 log_group_name=f"/aws/lambda/{function_name}",
                 retention=RetentionDays.THREE_MONTHS,
                 removal_policy=RemovalPolicy.DESTROY)

        function = Function(self, "FromEvent",
                            function_name=function_name,
                            description="Persist activity records",
                            handler="on_activity_handler.handle_record",
                            **parameters)

        Rule(self, "EventRule",
             description="Route events from SPA to listening lambda function",
             event_pattern=EventPattern(
                 source=['SustainablePersonalAccounts'],
                 detail={"Environment": [toggles.environment_identifier]},
                 detail_type=Events.ACTIVITY_EVENT_LABELS),
             targets=[LambdaFunction(function)])

        return function

    def monthly(self, parameters) -> Function:

        function_name = toggles.environment_identifier + "OnMonthlyActivitiesReport"

        LogGroup(self, function_name + "Log",
                 log_group_name=f"/aws/lambda/{function_name}",
                 retention=RetentionDays.THREE_MONTHS,
                 removal_policy=RemovalPolicy.DESTROY)

        function = Function(self, "Monthly",
                            function_name=function_name,
                            description="Report activities from previous month",
                            handler="on_activity_handler.handle_monthly_report",
                            **parameters)

        Rule(self, "TriggerMonthly",
             rule_name="{}OnMonthlyActivitiesReportTriggerRule".format(toggles.environment_identifier),
             description="Trigger monthly reporting on activities",
             schedule=Schedule.cron(day="1", hour="3", minute="42"),
             targets=[LambdaFunction(function)])

        return function

    def daily(self, parameters) -> Function:

        function_name = toggles.environment_identifier + "OnDailyActivitiesReport"

        LogGroup(self, function_name + "Log",
                 log_group_name=f"/aws/lambda/{function_name}",
                 retention=RetentionDays.THREE_MONTHS,
                 removal_policy=RemovalPolicy.DESTROY)

        function = Function(self, "Daily",
                            function_name=function_name,
                            description="Report ongoing activities",
                            handler="on_activity_handler.handle_daily_report",
                            **parameters)

        Rule(self, "TriggerDaily",
             rule_name="{}OnDailyActivitiesReportTriggerRule".format(toggles.environment_identifier),
             description="Trigger daily reporting on activities",
             schedule=Schedule.cron(hour="2", minute="42"),
             targets=[LambdaFunction(function)])

        return function
