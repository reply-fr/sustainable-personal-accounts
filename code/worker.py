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
    def get_session(cls, account, session=None):
        arn = os.environ.get('ROLE_ARN_TO_MANAGE_ACCOUNTS')
        master = make_session(role_arn=arn, session=session) if arn else Session()

        name = os.environ.get('ROLE_NAME_TO_MANAGE_CODEBUILD', 'AWSControlTowerExecution')
        return make_session(role_arn=f'arn:aws:iam::{account}:role/{name}',
                            session=master)

    @classmethod
    def deploy_role(cls, name, session=None):
        return 'some_role'

    @classmethod
    def get_buildspec_for_prepare(cls):
        logging.debug("Getting buildspec for prepare")
        return BUILDSPEC_PREPARE

    @classmethod
    def get_buildspec_for_purge(cls):
        logging.debug("Getting buildspec for purge")
        return BUILDSPEC_PREPARE

    @classmethod
    def deploy_project(cls, name, description, buildspec, role, session=None):
        logging.debug("Deploying Codebuild project")

        session = session if session else Session()
        result = session.client('codebuild').create_project(
            name=name,
            description=description,
            source=dict(type='NO_SOURCE',
                        buildspec=buildspec),
            artifacts=dict(type='NO_ARTIFACTS'),
            cache=dict(type='NO_CACHE'),
            environment=dict(type='ARM_CONTAINER',
                             image='aws/codebuild/amazonlinux2-aarch64-standard:2.0',
                             computeType='BUILD_GENERAL1_SMALL'),
            serviceRole=role,
            timeoutInMinutes=480,
            tags=[dict(key='origin', value='SustainablePersonalAccounts')],
            logsConfig=dict(cloudWatchLogs=dict(status='ENABLED')),
            concurrentBuildLimit=1)
        logging.debug("Done")
        return result['project']['arn']

    @classmethod
    def build_project(cls, arn, session=None):
        logging.debug("Starting project build with Codebuild ")
        # session.client('codebuild').start_build( ... )
        pass

    @classmethod
    def prepare(cls, account, session=None):
        session = session if session else cls.get_session(account)

        logging.info(f"Preparing account '{account}'...")
        buildspec = cls.get_buildspec_for_prepare()
        role = cls.deploy_role(name='SpaRoleForCodebuild', session=session)
        arn = cls.deploy_project(name="SpaProjectForPrepare",
                                 description="This project prepares an AWS account before being released to cloud engineer",
                                 buildspec=buildspec,
                                 role=role,
                                 session=session)
        cls.build_project(arn=arn, session=session)
        logging.info("Done")

        # to be moved to the end of the Codebuild buildspec
        Events.emit('PreparedAccount', account)

    @classmethod
    def purge(cls, account, session=None):
        session = session if session else cls.get_session(account)

        logging.info(f"Purging account '{account}'...")
        buildspec = cls.get_buildspec_for_purge()
        role = cls.deploy_role(name='SpaRoleForCodebuild', session=session)
        arn = cls.deploy_project(name="SpaProjectForPurge",
                                 description="This project purges an AWS account of cloud resources",
                                 buildspec=buildspec,
                                 role=role,
                                 session=session)
        cls.build_project(arn=arn, session=session)
        logging.info("Done")

        # to be moved to the end of the Codebuild buildspec
        Events.emit('PurgedAccount', account)
