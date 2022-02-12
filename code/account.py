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

from enum import Enum, unique
import os

from boto3.session import Session


@unique
class State(Enum):
    VANILLA = 'vanilla'
    ASSIGNED = 'assigned'
    RELEASED = 'released'
    EXPIRED = 'expired'


class Account:

    @classmethod
    def move(cls, account, state: State, session=None):
        if not isinstance(state, State):
            raise ValueError(f"Unexpected state type {state}")

        if os.environ.get("DRY_RUN") == "true":
            return

        session = session if session else Session()
        session.client('organizations').tag_resource(
            ResourceId=account,
            Tags=[dict(Key='account:state', Value=state.value)])
