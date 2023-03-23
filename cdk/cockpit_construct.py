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
from aws_cdk import Duration
from aws_cdk.aws_cloudwatch import (Dashboard,
                                    GraphWidget,
                                    MathExpression,
                                    TextWidget)


class Cockpit(Construct):

    def __init__(self, scope: Construct, id: str, functions, tables):
        super().__init__(scope, id)

        self.cockpit = Dashboard(self, id=id, dashboard_name=id)

        self.cockpit.add_widgets(
            self.get_text_label_widget())

        self.cockpit.add_widgets(
            self.get_costs_by_cost_center_widget(),
            self.get_transactions_by_cost_center_widget(),
            self.get_transactions_by_label_widget())

        self.cockpit.add_widgets(
            self.get_events_by_label_widget(),
            self.get_exceptions_by_label_widget())

        self.cockpit.add_widgets(
            self.get_lambda_invocations_widget(functions=functions),
            self.get_lambda_durations_widget(functions=functions),
            self.get_lambda_errors_widget(functions=functions))

        self.cockpit.add_widgets(
            # self.get_dynamodb_request_latency_widget(tables=tables),
            self.get_dynamodb_read_capacity_units_widget(tables=tables),
            self.get_dynamodb_write_capacity_units_widget(tables=tables),
            self.get_dynamodb_system_errors_widget(tables=tables),
            self.get_dynamodb_user_errors_widget(tables=tables))

    SEARCH_TEMPLATE = "SEARCH('{SustainablePersonalAccount, ___by___, Environment} Environment=""___environment___"" MetricName=""___metric___""', 'Sum', 60)"

    def get_search_expression(self, by='Account', environment=None, metric=None):
        environment = environment or toggles.environment_identifier
        metric = metric or f"AccountEventsBy{by}"
        return self.SEARCH_TEMPLATE.replace('___by___', by).replace('___environment___', environment).replace('___metric___', metric)

    def get_text_label_widget(self):
        ''' show static banner that has been configured for this dashboard '''
        return TextWidget(markdown=toggles.automation_cockpit_markdown_text,
                          height=3,
                          width=24)

    def get_costs_by_cost_center_widget(self):
        return GraphWidget(
            title="Daily costs by cost center",
            left=[MathExpression(expression=self.get_search_expression(by='CostCenter', metric='DailyCostByCostCenter'),
                                 label='',
                                 period=Duration.days(1))],
            left_y_axis=dict(label='USD'),
            stacked=True,
            height=6,
            width=8)

    def get_transactions_by_cost_center_widget(self):
        return GraphWidget(
            title="Transactions by cost center",
            left=[MathExpression(expression=self.get_search_expression(by='CostCenter', metric='TransactionsByCostCenter'),
                                 label='',
                                 period=Duration.minutes(5))],
            left_y_axis=dict(show_units=False),
            stacked=True,
            height=6,
            width=8)

    def get_transactions_by_label_widget(self):
        return GraphWidget(
            title="Transactions by label",
            left=[MathExpression(expression=self.get_search_expression(by='Label', metric='TransactionsByLabel'),
                                 label='',
                                 period=Duration.minutes(5))],
            left_y_axis=dict(show_units=False),
            stacked=True,
            height=6,
            width=8)

    def get_events_by_label_widget(self):
        return GraphWidget(
            title="Events by label",
            left=[MathExpression(expression=self.get_search_expression(by='Label', metric='AccountEventsByLabel'),
                                 label='',
                                 period=Duration.minutes(5))],
            left_y_axis=dict(show_units=False),
            stacked=True,
            height=6,
            width=12)

    def get_exceptions_by_label_widget(self):
        return GraphWidget(
            title="Exceptions by label",
            left=[MathExpression(expression=self.get_search_expression(by='Label', metric='ExceptionsByLabel'),
                                 label='',
                                 period=Duration.minutes(5))],
            left_y_axis=dict(show_units=False),
            stacked=True,
            height=6,
            width=12)

    def get_lambda_invocations_widget(self, functions):
        return GraphWidget(title="Lambda invocations",
                           left=[x.metric_invocations() for x in functions],
                           left_y_axis=dict(show_units=False),
                           stacked=True,
                           width=8)

    def get_lambda_durations_widget(self, functions):
        return GraphWidget(title="Lambda durations",
                           left=[x.metric_duration() for x in functions],
                           left_y_axis=dict(show_units=False),
                           stacked=True,
                           width=8)

    def get_lambda_errors_widget(self, functions):
        return GraphWidget(title="Lambda errors",
                           left=[x.metric_errors() for x in functions],
                           left_y_axis=dict(show_units=False),
                           stacked=True,
                           width=8)

    # def get_dynamodb_request_latency_widget(self, tables):
    #     return GraphWidget(title="DynamoDB latency",
    #                        left=[x.metric_successful_request_latency() for x in tables],
    #                        left_y_axis=dict(show_units=False),
    #                        stacked=True,
    #                        width=8)

    def get_dynamodb_read_capacity_units_widget(self, tables):
        return GraphWidget(title="DynamoDB read capacity units",
                           left=[x.metric_consumed_read_capacity_units() for x in tables],
                           left_y_axis=dict(show_units=False),
                           stacked=True,
                           width=6)

    def get_dynamodb_write_capacity_units_widget(self, tables):
        return GraphWidget(title="DynamoDB write capacity units",
                           left=[x.metric_consumed_write_capacity_units() for x in tables],
                           left_y_axis=dict(show_units=False),
                           stacked=True,
                           width=6)

    def get_dynamodb_system_errors_widget(self, tables):
        return GraphWidget(title="DynamoDB errors",
                           left=[x.metric_system_errors_for_operations() for x in tables],
                           left_y_axis=dict(show_units=False),
                           stacked=True,
                           width=6)

    def get_dynamodb_user_errors_widget(self, tables):
        return GraphWidget(title="DynamoDB errors",
                           left=[x.metric_user_errors() for x in tables],
                           left_y_axis=dict(show_units=False),
                           stacked=True,
                           width=6)
