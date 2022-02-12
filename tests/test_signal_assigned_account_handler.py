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

import logging
logging.getLogger('botocore').setLevel(logging.CRITICAL)
logging.getLogger('urllib3').setLevel(logging.CRITICAL)

from unittest.mock import patch
import os
import pytest

from code import EventFactory, State
from code.signal_assigned_account_handler import handler


pytestmark = pytest.mark.wip


def test_handler():

    with patch.dict(os.environ, dict(DRY_RUN="true")):

        event = EventFactory.make_event(template="tests/events/tag-account-template.json",
                                        context=dict(account="123456789012",
                                                     new_state=State.ASSIGNED.value))
        result = handler(event=event, context=None)
        assert result == 'AssignedAccount 123456789012'

        event = EventFactory.make_event(template="tests/events/tag-account-template.json",
                                        context=dict(account="123456789012",
                                                     new_state=State.VANILLA.value))
        with pytest.raises(ValueError):
            handler(event=event, context=None)
