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
import os


class Datastore:
    instance = None

    @classmethod
    def get_instance(cls, path=None):
        path = path or os.environ.get('DATASTORE_PATH', 'memory:')
        logging.debug(f"Looking for datastore '{path}")

        if path == 'memory:':
            if not cls.instance:
                cls.instance = MemoryDatastore()
            return cls.instance

        raise AttributeError(f"Unknown datastore path '{path}")


class MemoryDatastore:

    def __init__(self):
        self.data = {}

    def forget(self, key):
        try:
            del self.data[key]
        except KeyError:
            pass

    def remember(self, key, value):
        self.data[key] = value

    def retrieve(self, key):
        return self.data.get(key)


datastore = Datastore.get_instance()
