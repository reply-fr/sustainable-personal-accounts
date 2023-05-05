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

        if toggles.features_with_cost_management_tag:

            self.cockpit.add_widgets(
                self.get_text_label_widget('top'))

            self.cockpit.add_widgets(
                self.get_costs_by_cost_center_widget(),
                self.get_transactions_by_cost_center_widget(),
                self.get_transactions_by_label_widget())

        else:  # alternate layout in absence of cost metric

            self.cockpit.add_widgets(
                self.get_text_label_widget('aside'),
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
            self.get_dynamodb_read_capacity_units_widget(),
            self.get_dynamodb_write_capacity_units_widget(),
            self.get_dynamodb_errors_widget())

    def get_search_expression(self, by=None, environment=None, metric=None, statistic=None, duration=None):
        expression = "SEARCH('{SustainablePersonalAccount, ___by___, Environment} Environment=""___environment___"" MetricName=""___metric___""', '___statistic___', ___duration___)"
        replacements = {'___by___': by or 'Account',
                        '___environment___': environment or toggles.environment_identifier,
                        '___metric___': metric or f"AccountEventsBy{by}",
                        '___statistic___': statistic or 'Sum',
                        '___duration___': duration or 60}
        for key in replacements.keys():
            expression = expression.replace(key, str(replacements[key]))
        return expression

    def get_text_label_widget(self, layout='top'):
        ''' show static banner that has been configured for this dashboard '''
        return TextWidget(markdown=toggles.automation_cockpit_markdown_text,
                          height=6 if layout == 'aside' else 2,
                          width=8 if layout == 'aside' else 24)

    def get_costs_by_cost_center_widget(self):
        return GraphWidget(
            title="Daily costs by cost center",
            left=[MathExpression(expression=self.get_search_expression(by='CostCenter',
                                                                       metric='DailyCostsByCostCenter',
                                                                       statistic='Maximum',
                                                                       duration=86400),
                                 label='',
                                 period=Duration.days(1))],
            left_y_axis=dict(label='USD'),
            stacked=True,
            height=6,
            width=8)

    def get_transactions_by_cost_center_widget(self):
        return GraphWidget(
            title="Transactions by cost center",
            left=[MathExpression(expression=self.get_search_expression(by='CostCenter',
                                                                       metric='TransactionsByCostCenter',
                                                                       duration=86400),
                                 label='',
                                 period=Duration.days(1))],
            left_y_axis=dict(show_units=False),
            stacked=True,
            height=6,
            width=8)

    def get_transactions_by_label_widget(self):
        return GraphWidget(
            title="Transactions by label",
            left=[MathExpression(expression=self.get_search_expression(by='Label',
                                                                       metric='TransactionsByLabel',
                                                                       duration=86400),
                                 label='',
                                 period=Duration.days(1))],
            left_y_axis=dict(show_units=False),
            stacked=False,
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

    def get_dynamodb_search_expression(self, metric=None, statistic=None, duration=None):
        expression = "SEARCH('{AWS/DynamoDB,TableName} MetricName=""___metric___""', '___statistic___', ___duration___)"
        replacements = {'___metric___': metric or "ConsumedReadCapacityUnits",
                        '___statistic___': statistic or 'Sum',
                        '___duration___': duration or 60}
        for key in replacements.keys():
            expression = expression.replace(key, str(replacements[key]))
        return expression

    def get_dynamodb_read_capacity_units_widget(self):
        return GraphWidget(title="DynamoDB read capacity units",
                           left=[MathExpression(expression=self.get_dynamodb_search_expression(metric='ConsumedReadCapacityUnits'),
                                                label='',
                                                period=Duration.minutes(5))],
                           left_y_axis=dict(show_units=False),
                           stacked=True,
                           width=8)

    def get_dynamodb_write_capacity_units_widget(self):
        return GraphWidget(title="DynamoDB write capacity units",
                           left=[MathExpression(expression=self.get_dynamodb_search_expression(metric='ConsumedWriteCapacityUnits'),
                                                label='',
                                                period=Duration.minutes(5))],
                           left_y_axis=dict(show_units=False),
                           stacked=True,
                           width=8)

    def get_dynamodb_errors_widget(self):
        return GraphWidget(title="DynamoDB errors",
                           left=[MathExpression(expression=self.get_dynamodb_search_expression(metric='SystemErrorsForOperations'),
                                                label='SystemErrorsForOperations',
                                                period=Duration.minutes(5)),
                                 MathExpression(expression=self.get_dynamodb_search_expression(metric='UserErrors'),
                                                label='UserErrors',
                                                period=Duration.minutes(5))],
                           left_y_axis=dict(show_units=False),
                           stacked=True,
                           width=8)
