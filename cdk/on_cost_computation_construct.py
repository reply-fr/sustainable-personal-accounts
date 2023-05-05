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
from aws_cdk.aws_events import Rule, Schedule
from aws_cdk.aws_events_targets import LambdaFunction
from aws_cdk.aws_lambda import Function
from aws_cdk.aws_logs import LogGroup, RetentionDays


class OnCostComputation(Construct):

    def __init__(self, scope: Construct, id: str, parameters={}) -> None:
        super().__init__(scope, id)

        if not toggles.features_with_cost_management_tag:  # do not deploy if cost management has not been activated
            self.functions = []
            return

        parameters['environment']['COST_MANAGEMENT_TAG'] = toggles.features_with_cost_management_tag
        parameters['environment']['REPORTING_COSTS_PREFIX'] = toggles.reporting_costs_prefix
        parameters['environment']['REPORTING_COSTS_MARKDOWN'] = toggles.reporting_costs_markdown_template
        if toggles.features_with_origin_email_recipient:
            parameters['environment']['ORIGIN_EMAIL_RECIPIENT'] = toggles.features_with_origin_email_recipient
        if toggles.features_with_cost_email_recipients:
            parameters['environment']['COST_EMAIL_RECIPIENTS'] = ', '.join(toggles.features_with_cost_email_recipients)

        self.functions = [self.monthly(parameters=parameters),
                          self.daily(parameters=parameters)]

    def monthly(self, parameters) -> Function:

        function_name = toggles.environment_identifier + "OnMonthlyCostsReport"

        LogGroup(self, function_name + "Log",
                 log_group_name=f"/aws/lambda/{function_name}",
                 retention=RetentionDays.THREE_MONTHS,
                 removal_policy=RemovalPolicy.DESTROY)

        function = Function(self, "Monthly",
                            function_name=function_name,
                            description="Report costs from previous month",
                            handler="on_cost_computation_handler.handle_monthly_reports",
                            memory_size=1024,  # accomodate for hundreds of accounts and related data
                            **parameters)

        Rule(self, "TriggerMonthly",
             rule_name="{}OnMonthlyCostsReportTriggerRule".format(toggles.environment_identifier),
             description="Trigger monthly reporting on costs",
             schedule=Schedule.cron(day="3", hour="2", minute="42"),
             targets=[LambdaFunction(function)])

        return function

    def daily(self, parameters) -> Function:

        function_name = toggles.environment_identifier + "OnDailyCostsMetric"

        LogGroup(self, function_name + "Log",
                 log_group_name=f"/aws/lambda/{function_name}",
                 retention=RetentionDays.THREE_MONTHS,
                 removal_policy=RemovalPolicy.DESTROY)

        function = Function(self, "Daily",
                            function_name=function_name,
                            description="Measure daily costs",
                            handler="on_cost_computation_handler.handle_daily_metrics",
                            **parameters)

        Rule(self, "TriggerDaily",
             rule_name="{}OnDailyCostsMetricTriggerRule".format(toggles.environment_identifier),
             description="Trigger daily cost computations",
             schedule=Schedule.cron(hour="11", minute="42"),
             targets=[LambdaFunction(function)])

        return function
