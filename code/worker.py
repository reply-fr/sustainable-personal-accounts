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

import json
import logging
import os

from boto3.session import Session

from events import Events
from session import make_session


BUILDSPEC_PREPARE = """
version: 0.2

phases:
  install:
    runtime-versions:
      python: 3.9
  pre_build:
    commands:
      - apt-get install -y wget
      - echo Nothing to do in the pre_build phase...
  build:
    commands:
      - echo Build started on `date`
      - python --version
      - aws --version
  post_build:
    commands:
      - echo Build completed on `date`
"""

class Worker:

    @classmethod
    def get_session(cls, account):
        arn = os.environ.get('ROLE_ARN_TO_MANAGE_ACCOUNTS')
        master = make_session(role_arn=arn) if arn else Session()

        name = os.environ.get('ROLE_NAME_TO_MANAGE_CODEBUILD', 'AWSControlTowerExecution')
        return make_session(role_arn=f'arn:aws:iam::{account}:role/{name}',
                            session=master)

    @classmethod
    def deploy_project(cls, buildspec, session=None):
        session = session if session else Session()
        session.client('codebuild').create_project(
            name='test',
            description="Fancy project",
            source=dict(type='NO_SOURCE'),
            buildspec=buildspec,
            artifacts=dict(type='NO_ARTIFACTS'),
            cache=dict(type='NO_CACHE'),
            environment=dict(type='ARM_CONTAINER',
                             image='aws/codebuild/amazonlinux2-aarch64-standard:2.0',
                             computeType='BUILD_GENERAL1_SMALL'),
            serviceRole='',
            timeoutInMinutes=480,
            tags=[dict(key='origin', value='SustainablePersonalAccounts')],
            logsConfig=dict(cloudWatchLogs=dict(status='ENABLED')),
            concurrentBuildLimit=1)

    @classmethod
    def prepare(cls, account, session=None):
        session = session if session else cls.get_session(account)

        logging.info(f"Preparing account '{account}'...")

        id = cls.deploy_project(stream='test', session=session)

        # session.client('codebuild').start_build( ... )

        logging.info("Done")

        # to be moved to the end of the Codebuild buildspec
        Events.emit('PreparedAccount', account)

    @classmethod
    def purge(cls, account, session=None):
        session = session if session else cls.get_session(account)

        logging.info(f"Purging account '{account}'...")

        # session.client('codebuild').create_project( ... )

        # session.client('codebuild').start_build( ... )

        logging.info("Done")

        # to be moved to the end of the Codebuild buildspec
        Events.emit('PurgedAccount', account)
