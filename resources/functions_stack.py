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
from aws_cdk import Stack
from aws_cdk.aws_iam import Effect, PolicyStatement

from .listen_account_events_construct import ListenAccountEventsConstruct
from .move_expired_accounts_construct import MoveExpiredAccountsConstruct
from .move_prepared_account_construct import MovePreparedAccountConstruct
from .move_purged_account_construct import MovePurgedAccountConstruct
from .move_vanilla_account_construct import MoveVanillaAccountConstruct
from .signal_assigned_account_construct import SignalAssignedAccountConstruct
from .signal_expired_account_construct import SignalExpiredAccountConstruct


class FunctionsStack(Stack):

    def __init__(self, scope: Construct, id: str) -> None:
        super().__init__(scope, id)

        statements = [

            PolicyStatement(  # allow to put events
                effect=Effect.ALLOW,
                actions=['events:PutEvents'],
                resources=['*']
            ),

            PolicyStatement(  # allow to put metrics
                effect=Effect.ALLOW,
                actions=['cloudwatch:PutMetricData'],
                resources=['*']
            )

        ]

        ListenAccountEventsConstruct(
            self, "ListenAccountEvents",
            statements=statements)
        MoveVanillaAccountConstruct(
            self, "MoveVanillaAccount",
            statements=statements)
        SignalAssignedAccountConstruct(
            self, "SignalAssignedAccount",
            statements=statements)
        MovePreparedAccountConstruct(
            self, "MovePreparedAccount",
            statements=statements)
        MoveExpiredAccountsConstruct(
            self, "MoveExpiredAccounts",
            statements=statements)
        SignalExpiredAccountConstruct(
            self, "SignalExpiredAccount",
            statements=statements)
        MovePurgedAccountConstruct(
            self, "MovePurgedAccount",
            statements=statements)
