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
from aws_cdk.aws_events import Rule, Schedule
from aws_cdk.aws_events_targets import LambdaFunction
from aws_cdk.aws_lambda import Function

from cdk import LoggingFunction


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
        if toggles.features_with_cost_extra_currencies:
            parameters['environment']['COST_EXTRA_CURRENCIES'] = ', '.join(toggles.features_with_cost_extra_currencies)
        parameters['memory_size'] = 1024  # accomodate for hundreds of accounts and related data

        self.functions = [self.report(parameters=parameters),
                          self.report_and_email(parameters=parameters),
                          self.meter(parameters=parameters)]

    def report(self, parameters) -> Function:

        function = LoggingFunction(self,
                                   name="OnEarlyCostReport",
                                   description="Report usage and support costs from previous month",
                                   trigger="EarlyMonthly",
                                   handler="on_cost_computation_handler.handle_monthly_reports",
                                   parameters=parameters)

        Rule(self, "TriggerEarly",
             rule_name="{}OnEarlyCostReportTriggerRule".format(toggles.environment_identifier),
             description="Trigger early monthly reporting on costs",
             schedule=Schedule.cron(day="6", hour="2", minute="42"),
             targets=[LambdaFunction(function)])

        return function

    def report_and_email(self, parameters) -> Function:

        function = LoggingFunction(self,
                                   name="OnMonthlyCostReport",
                                   description="Report finalized costs from previous month",
                                   trigger="LateMonthly",
                                   handler="on_cost_computation_handler.handle_monthly_reports_and_emails",
                                   parameters=parameters)

        Rule(self, "TriggerMonthly",
             rule_name="{}OnMonthlyCostReportTriggerRule".format(toggles.environment_identifier),
             description="Trigger final monthly reporting on costs",
             schedule=Schedule.cron(day="14", hour="2", minute="42"),
             targets=[LambdaFunction(function)])

        return function

    def meter(self, parameters) -> Function:

        function = LoggingFunction(self,
                                   name="OnDailyCostsMetric",
                                   description="Measure daily usage and support costs",
                                   trigger="Daily",
                                   handler="on_cost_computation_handler.handle_daily_metrics",
                                   parameters=parameters)

        Rule(self, "TriggerDaily",
             rule_name="{}OnDailyCostsMetricTriggerRule".format(toggles.environment_identifier),
             description="Trigger daily cost computations",
             schedule=Schedule.cron(hour="0", minute="42"),
             targets=[LambdaFunction(function)])

        return function
