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

from io import StringIO
from unittest.mock import Mock
import pytest

from code import setup_logging, trap_exception


pytestmark = pytest.mark.wip


def write_to(log):
    log.critical('critical')
    log.error('error')
    log.warning('warning')
    log.info('info')
    log.debug('debug')


def test_setup_logging():
    stream = StringIO()
    log = setup_logging(name='logger_for_critical',
                        stream=stream)
    log.critical('critical')
    stream.seek(0)
    assert stream.read() == '[CRITICAL] critical\n'


def test_setup_logging_for_critical():
    stream = StringIO()
    log = setup_logging(environ=dict(VERBOSITY='CRITICAL'),
                        name='logger_for_critical',
                        stream=stream)
    write_to(log)
    stream.seek(0)
    assert stream.read() == '[CRITICAL] critical\n'


def test_setup_logging_for_error():
    stream = StringIO()
    log = setup_logging(environ=dict(VERBOSITY='ERROR'),
                        name='logger_for_error',
                        stream=stream)
    write_to(log)
    stream.seek(0)
    assert stream.read() == '[CRITICAL] critical\n[ERROR] error\n'


def test_setup_logging_for_warning():
    stream = StringIO()
    log = setup_logging(environ=dict(VERBOSITY='WARNING'),
                        name='logger_for_warning',
                        stream=stream)
    write_to(log)
    stream.seek(0)
    assert stream.read() == '[CRITICAL] critical\n[ERROR] error\n[WARNING] warning\n'


def test_setup_logging_for_info():
    stream = StringIO()
    log = setup_logging(environ=dict(VERBOSITY='INFO'),
                        name='logger_for_info',
                        stream=stream)
    write_to(log)
    stream.seek(0)
    assert stream.read() == '[CRITICAL] critical\n[ERROR] error\n[WARNING] warning\n[INFO] info\n'


def test_setup_logging_for_debug():
    stream = StringIO()
    log = setup_logging(environ=dict(VERBOSITY='DEBUG'),
                        name='logger_for_debug',
                        stream=stream)
    write_to(log)
    stream.seek(0)
    assert stream.read() == '[CRITICAL] critical\n[ERROR] error\n[WARNING] warning\n[INFO] info\n[DEBUG] debug\n'


def test_trap_exception_on_no_error():
    mock = Mock(return_value='ok')
    decorated = trap_exception(mock)
    result = decorated(1, 2, a='b', c='d')
    mock.assert_called_with(1, 2, a='b', c='d')
    assert result == 'ok'


def test_trap_exception_on_value_error():
    mock = Mock(side_effect=ValueError('boom'))
    decorated = trap_exception(mock)
    result = decorated(1, 2, a='b', c='d')
    mock.assert_called_with(1, 2, a='b', c='d')
    assert result == "[DEBUG] boom"


def test_trap_exception_on_internal_error():
    mock = Mock(side_effect=RuntimeError('boom'))
    decorated = trap_exception(mock)
    result = decorated(1, 2, a='b', c='d')
    mock.assert_called_with(1, 2, a='b', c='d')
    assert result == "[ERROR] RuntimeError: boom"
