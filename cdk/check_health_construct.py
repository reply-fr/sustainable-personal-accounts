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
from aws_cdk.aws_lambda import Function
from aws_cdk.aws_logs import LogGroup, RetentionDays


class CheckHealth(Construct):

    def __init__(self, scope: Construct, id: str, parameters={}) -> None:
        super().__init__(scope, id)
        self.functions = [self.on_run(parameters=parameters)]

    def on_run(self, parameters) -> Function:

        function_name = toggles.environment_identifier + "CheckHealth"

        LogGroup(self, function_name + "Log",
                 log_group_name=f"/aws/lambda/{function_name}",
                 retention=RetentionDays.THREE_MONTHS,
                 removal_policy=RemovalPolicy.DESTROY)

        return Function(
            self, "FromInvoke",
            function_name=function_name,
            description="Check the internal state of run-time",
            handler="check_health_handler.handle_event",
            **parameters)
