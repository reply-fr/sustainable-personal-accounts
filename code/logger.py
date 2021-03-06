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
# - https://towardsdatascience.com/the-reusable-python-logging-template-for-all-your-data-science-apps-551697c8540

import logging
logging.getLogger('botocore').setLevel(logging.CRITICAL)
logging.getLogger('urllib3').setLevel(logging.CRITICAL)

import functools
import os
import sys

LOGGING_FORMAT = "[%(levelname)s] %(message)s"


def setup_logging(environ=None,
                  format=LOGGING_FORMAT,
                  name=None,
                  stream=sys.stdout):
    logger = logging.getLogger(name)
    environ = environ or os.environ
    verbosity = environ.get('VERBOSITY', 'INFO')
    logger.setLevel(logging.__dict__[verbosity])
    handler = logging.StreamHandler(stream)
    handler.setFormatter(logging.Formatter(format))
    logger.handlers.clear()
    logger.addHandler(handler)
    return logger


def trap_exception(function):

    @functools.wraps(function)
    def safe_function(*args, **kwargs):
        try:
            return function(*args, **kwargs)

        except ValueError as error:  # regular code breaks, e.g., event is not for this specific function
            if os.environ.get('VERBOSITY', 'DEBUG') != 'DEBUG':
                logging.error(error)
            else:
                logging.exception(error)
            return f"[DEBUG] {error}"

        except Exception as error:  # prevent lambda retries on internal errors
            logging.exception(error)
            return f"[ERROR] {type(error).__name__}: {error}"

    return safe_function
