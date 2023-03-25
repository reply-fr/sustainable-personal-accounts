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


class OnCostComputation(Construct):

    def __init__(self, scope: Construct, id: str, parameters={}, permissions=[]) -> None:
        super().__init__(scope, id)

        if not toggles.features_with_cost_management_tag:  # do not deploy if cost management has not been activated
            self.functions = []
            return

        parameters['environment']['REPORTING_COSTS_PREFIX'] = toggles.reporting_costs_prefix
        parameters['environment']['COST_MANAGEMENT_TAG'] = toggles.features_with_cost_management_tag
        self.functions = [self.monthly(parameters=parameters, permissions=permissions),
                          self.daily(parameters=parameters, permissions=permissions)]

    def monthly(self, parameters, permissions) -> Function:

        function = Function(self, "Monthly",
                            function_name="{}OnMonthlyCostsReport".format(toggles.environment_identifier),
                            description="Report costs from previous month",
                            handler="on_cost_computation_handler.handle_monthly_report",
                            memory_size=1024,  # accomodate for hundreds of accounts and related data
                            **parameters)

        for permission in permissions:
            function.add_to_role_policy(permission)

        Rule(self, "TriggerMonthly",
             rule_name="{}OnMonthlyCostsReportTriggerRule".format(toggles.environment_identifier),
             description="Trigger monthly reporting on costs",
             schedule=Schedule.cron(day="1", hour="4", minute="42"),
             targets=[LambdaFunction(function)])

        return function

    def daily(self, parameters, permissions) -> Function:

        function = Function(self, "Daily",
                            function_name="{}OnDailyCostsMetric".format(toggles.environment_identifier),
                            description="Measure daily costs",
                            handler="on_cost_computation_handler.handle_daily_metric",
                            **parameters)

        for permission in permissions:
            function.add_to_role_policy(permission)

        Rule(self, "TriggerDaily",
             rule_name="{}OnDailyCostsMetricTriggerRule".format(toggles.environment_identifier),
             description="Trigger daily cost computations",
             schedule=Schedule.cron(hour="1", minute="42"),
             targets=[LambdaFunction(function)])

        return function
