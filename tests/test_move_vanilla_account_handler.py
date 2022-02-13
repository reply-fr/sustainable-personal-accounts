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
from code.move_vanilla_account_handler import handle_move_event, handle_tag_event


# pytestmark = pytest.mark.wip


@patch.dict(os.environ, dict(DRY_RUN="true"))
def test_handle_move_event():
    event = EventFactory.make_event(template="tests/events/move-account-template.json",
                                    context=dict(account="123456789012",
                                                 destination_organizational_unit="ou-landing",
                                                 origin_organizational_unit="ou-origin"))
    with patch.dict(os.environ, dict(ORGANIZATIONAL_UNIT="ou-landing")):
        result = handle_move_event(event=event, context=None)
    assert result == {'Detail': '{"Account": "123456789012"}', 'DetailType': 'CreatedAccount', 'Source': 'SustainablePersonalAccounts'}


@patch.dict(os.environ, dict(DRY_RUN="true"))
def test_handle_move_event_on_unexpected_event():
    event = EventFactory.make_event(template="tests/events/move-account-template.json",
                                    context=dict(account="123456789012",
                                                 destination_organizational_unit="ou-unexpected",
                                                 origin_organizational_unit="ou-origin"))
    with patch.dict(os.environ, dict(ORGANIZATIONAL_UNIT="ou-landing")):
        with pytest.raises(ValueError):
            handle_move_event(event=event, context=None)


@patch.dict(os.environ, dict(DRY_RUN="true"))
def test_handle_tag_event():
    event = EventFactory.make_event(template="tests/events/tag-account-template.json",
                                    context=dict(account="123456789012",
                                                 new_state=State.VANILLA.value))
    result = handle_tag_event(event=event, context=None)
    assert result == {'Detail': '{"Account": "123456789012"}', 'DetailType': 'CreatedAccount', 'Source': 'SustainablePersonalAccounts'}


@patch.dict(os.environ, dict(DRY_RUN="true"))
def test_handle_tag_event_on_unexpected_event():
    event = EventFactory.make_event(template="tests/events/tag-account-template.json",
                                    context=dict(account="123456789012",
                                                 new_state=State.ASSIGNED.value))
    with pytest.raises(ValueError):
        handle_tag_event(event=event, context=None)
