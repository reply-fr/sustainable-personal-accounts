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
from aws_cdk.aws_dynamodb import AttributeType, BillingMode, Table
from aws_cdk.aws_events import EventPattern, Rule, Schedule
from aws_cdk.aws_events_targets import LambdaFunction
from aws_cdk.aws_lambda import Function

from code import Events


class OnRecord(Construct):

    def __init__(self, scope: Construct, id: str, parameters={}, permissions=[]) -> None:
        super().__init__(scope, id)

        parameters['environment']['METERING_RECORDS_DATASTORE'] = toggles.metering_records_datastore
        parameters['environment']['METERING_RECORDS_TTL'] = str(toggles.metering_records_ttl_in_seconds)
        parameters['environment']['REPORTING_ACTIVITIES_PREFIX'] = toggles.reporting_activities_prefix
        self.functions = [self.on_event(parameters=parameters, permissions=permissions),
                          self.monthly(parameters=parameters, permissions=permissions),
                          self.daily(parameters=parameters, permissions=permissions)]

        self.table = Table(
            self, "RecordsTable",
            table_name=toggles.metering_records_datastore,
            partition_key={'name': 'Identifier', 'type': AttributeType.STRING},
            sort_key={'name': 'Order', 'type': AttributeType.STRING},
            billing_mode=BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY,
            time_to_live_attribute="Expiration")

        for function in self.functions:
            self.table.grant_read_write_data(grantee=function)

    def on_event(self, parameters, permissions) -> Function:

        function = Function(self, "FromEvent",
                            function_name="{}OnRecord".format(toggles.environment_identifier),
                            description="Persist records",
                            handler="on_record_handler.handle_record",
                            **parameters)

        for permission in permissions:
            function.add_to_role_policy(permission)

        Rule(self, "EventRule",
             description="Route events from SPA to listening lambda function",
             event_pattern=EventPattern(
                 source=['SustainablePersonalAccounts'],
                 detail={"Environment": [toggles.environment_identifier]},
                 detail_type=Events.RECORD_EVENT_LABELS),
             targets=[LambdaFunction(function)])

        return function

    def monthly(self, parameters, permissions) -> Function:

        function = Function(self, "Monthly",
                            function_name="{}OnMonthlyActivitiesReporting".format(toggles.environment_identifier),
                            description="Report activities from previous month",
                            handler="on_record_handler.handle_monthly_reporting",
                            **parameters)

        for permission in permissions:
            function.add_to_role_policy(permission)

        Rule(self, "TriggerMonthly",
             rule_name="{}OnMonthlyActivitiesReportingTriggerRule".format(toggles.environment_identifier),
             description="Trigger monthly reporting on activities",
             schedule=Schedule.cron(day="1", hour="3", minute="42"),
             targets=[LambdaFunction(function)])

        return function

    def daily(self, parameters, permissions) -> Function:

        function = Function(self, "Daily",
                            function_name="{}OnDailyActivitiesReporting".format(toggles.environment_identifier),
                            description="Report ongoing activities",
                            handler="on_record_handler.handle_daily_reporting",
                            **parameters)

        for permission in permissions:
            function.add_to_role_policy(permission)

        Rule(self, "TriggerDaily",
             rule_name="{}OnDailyActivitiesReportingTriggerRule".format(toggles.environment_identifier),
             description="Trigger daily reporting on activities",
             schedule=Schedule.cron(hour="2", minute="42"),
             targets=[LambdaFunction(function)])

        return function
