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
from aws_cdk.aws_dynamodb import AttributeType, BillingMode, Table, StreamViewType
from aws_cdk.aws_events import EventPattern, Rule
from aws_cdk.aws_events_targets import LambdaFunction
from aws_cdk.aws_lambda import Function, StartingPosition
from aws_cdk.aws_lambda_event_sources import DynamoEventSource

from code import Events


class OnAccountEventThenMeter(Construct):

    def __init__(self, scope: Construct, id: str, parameters={}, permissions=[]) -> None:
        super().__init__(scope, id)

        self.table = Table(
            self, "TransactionsTable",
            table_name=toggles.metering_transactions_datastore,
            partition_key={'name': 'Identifier', 'type': AttributeType.STRING},
            sort_key={'name': 'Order', 'type': AttributeType.STRING},
            billing_mode=BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY,
            stream=StreamViewType.NEW_AND_OLD_IMAGES,
            time_to_live_attribute="Expiration")

        parameters['environment']['METERING_TRANSACTIONS_DATASTORE'] = toggles.metering_transactions_datastore
        parameters['environment']['METERING_TRANSACTIONS_TTL'] = str(toggles.metering_transactions_ttl_in_seconds)
        self.functions = [self.on_event(parameters=parameters, permissions=permissions),
                          self.on_stream(parameters=parameters, permissions=permissions, table=self.table)]

        for function in self.functions:
            self.table.grant_read_write_data(grantee=function)

    def on_event(self, parameters, permissions) -> Function:

        function = Function(self, "FromEvent",
                            function_name="{}OnAccountEventsThenMeter".format(toggles.environment_identifier),
                            description="Turn events to transactions",
                            handler="on_account_event_then_meter_handler.handle_account_event",
                            **parameters)

        for permission in permissions:
            function.add_to_role_policy(permission)

        Rule(self, "EventRule",
             description="Route events from SPA to listening lambda function",
             event_pattern=EventPattern(
                 source=['SustainablePersonalAccounts'],
                 detail={"Environment": [toggles.environment_identifier]},
                 detail_type=Events.ACCOUNT_EVENT_LABELS),
             targets=[LambdaFunction(function)])

        return function

    def on_stream(self, parameters, permissions, table) -> Function:

        function = Function(self, "FromStream",
                            function_name="{}OnMeteringStream".format(toggles.environment_identifier),
                            description="Process metering stream",
                            handler="on_account_event_then_meter_handler.handle_stream_event",
                            **parameters)

        for permission in permissions:
            function.add_to_role_policy(permission)

        function.add_event_source(DynamoEventSource(  # stream items that have expired
            table,
            # filters=[{ "userIdentity": { "type": [ "Service" ] ,"principalId": ["dynamodb.amazonaws.com"] }}],
            starting_position=StartingPosition.TRIM_HORIZON))

        return function
