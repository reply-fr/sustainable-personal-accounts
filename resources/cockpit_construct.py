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

# credit:
# - https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_cloudwatch.Metric.html
# - https://medium.com/dtlpub/custom-cloudwatch-dashboard-to-monitor-lambdas-e399ef251f07
# - https://github.com/cdk-patterns/serverless/blob/main/the-cloudwatch-dashboard/python/the_cloudwatch_dashboard/the_cloudwatch_dashboard_stack.py


from constructs import Construct
from aws_cdk.aws_cloudwatch import (Dashboard,
                                    GraphWidget,
                                    Metric,
                                    TextWidget)

from code import State


class Cockpit(Construct):

    def __init__(self, scope: Construct, id: str, functions):
        super().__init__(scope, id)

        self.cockpit = Dashboard(
            self,
            id=id,
            dashboard_name=id)

        self.cockpit.add_widgets(
            self.get_text_label_widget())

        self.cockpit.add_widgets(
            self.get_events_by_state_widget(),
            self.get_events_by_account_widget())

        self.cockpit.add_widgets(
            self.get_lambda_invocations_widget(functions=functions),
            self.get_lambda_durations_widget(functions=functions),
            self.get_lambda_errors_widget(functions=functions))

    def get_text_label_widget(self):
        ''' show static banner that has been configured for this dashboard '''

        return TextWidget(markdown=toggles.automation_cockpit_markdown_text,
                          height=3,
                          width=24)

    def get_events_by_account_widget(self):

        return GraphWidget(
            title="Events by account",
            left=[Metric(
                namespace="SustainablePersonalAccount",
                metric_name="Account Event By Account",
                statistic="sum")],
            height=10,
            width=12)

    def get_events_by_state_widget(self):

        metrics = []
        for state in State:
            metrics.append(Metric(
                namespace="SustainablePersonalAccount",
                metric_name="Account Event By State",
                dimensions_map=dict(Label=state.value),
                statistic="sum"))

        return GraphWidget(
            title="Events by state",
            left=metrics,
            height=10,
            width=12)

    def get_lambda_durations_widget(self, functions):
        return GraphWidget(title="Lambda Durations",
                           width=8,
                           stacked=True,
                           left=[x.metric_duration() for x in functions])

    def get_lambda_errors_widget(self, functions):
        return GraphWidget(title="Lambda Errors",
                           width=8,
                           stacked=True,
                           left=[x.metric_errors() for x in functions])

    def get_lambda_invocations_widget(self, functions):
        return GraphWidget(title="Lambda Invocations",
                           width=8,
                           stacked=True,
                           left=[x.metric_invocations() for x in functions])
