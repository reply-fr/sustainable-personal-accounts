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
import time

from botocore.exceptions import ClientError
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
      - yum install -y wget
      - echo "Nothing to do in the pre_build phase..."
  build:
    commands:
      - echo "Build started on `date`"
      - python --version
      - aws --version
  post_build:
    commands:
      - echo "Build completed on `date`"
"""


class Worker:

    @classmethod
    def get_session(cls, account, session=None):
        arn = os.environ.get('ROLE_ARN_TO_MANAGE_ACCOUNTS')
        master = make_session(role_arn=arn, session=session) if arn else Session()

        name = os.environ.get('ROLE_NAME_TO_MANAGE_CODEBUILD', 'AWSControlTowerExecution')
        target = make_session(role_arn=f'arn:aws:iam::{account}:role/{name}',
                              session=master)
        identity = target.client('sts').get_caller_identity()
        logging.debug(f"identity {identity}")
        return target

    @classmethod
    def get_trusting_policy_document(cls):
        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "codebuild.amazonaws.com"
                    },
                    "Action": "sts:AssumeRole"
                }
            ]
        }
        return json.dumps(policy)

    @classmethod
    def deploy_role(cls, name, policy="AdministratorAccess", session=None):
        session = session if session else Session()
        iam = session.client('iam')

        logging.info(f"Deploying role '{name}' for projects")

        try:
            iam.create_role(
                RoleName=name,
                AssumeRolePolicyDocument=cls.get_trusting_policy_document(),
                Description='This is a test role',
                MaxSessionDuration=12 * 60 * 60,
                Tags=[dict(Key='owner', Value='SPA')])
            logging.debug(f"Role '{name}' has been created")
        except ClientError as error:
            if error.response['Error']['Code'] == 'EntityAlreadyExists':
                logging.debug(f"Role '{name}' already exists")
            else:
                logging.error(error)
                return

        try:
            iam.attach_role_policy(
                RoleName=name,
                PolicyArn=f"arn:aws:iam::aws:policy/{policy}")
            logging.debug(f"Policy '{policy}' has been attached to the role")
        except ClientError as error:
            logging.error(error)
            return

        waiter = iam.get_waiter('role_exists')
        waiter.wait(RoleName=name)

        role = iam.get_role(RoleName=name)
        logging.info("Done")
        return role['Role']['Arn']

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
        session = session if session else Session()
        client = session.client('codebuild')
        logging.debug("Deploying Codebuild project")
        retries = 10
        while retries > 0:  # we may have to wait for IAM role to be really available
            try:
                client.create_project(
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
                break

            except client.exceptions.ResourceAlreadyExistsException as error:
                logging.debug(f"Project '{name}' already exists")
                break

            except client.exceptions.InvalidInputException as error:
                logging.debug("Sleeping...")
                time.sleep(3)
                retries -= 1

    @classmethod
    def build_project(cls, name, session=None):
        session = session if session else Session()
        client = session.client('codebuild')
        logging.debug("Starting project build")
        client.start_build(projectName=name)

    @classmethod
    def prepare(cls, account, session=None):
        session = session if session else cls.get_session(account)

        logging.info(f"Preparing account '{account}'...")
        name = "SpaProjectForPrepare"
        buildspec = cls.get_buildspec_for_prepare()
        role = cls.deploy_role(name='SpaRoleForCodebuild', session=session)
        cls.deploy_project(name=name,
                           description="This project prepares an AWS account before being released to cloud engineer",
                           buildspec=buildspec,
                           role=role,
                           session=session)
        cls.build_project(name=name, session=session)
        logging.info("Done")

        # to be moved to the end of the Codebuild buildspec
        Events.emit('PreparedAccount', account)

    @classmethod
    def purge(cls, account, session=None):
        session = session if session else cls.get_session(account)

        logging.info(f"Purging account '{account}'...")
        name = "SpaProjectForPurge"
        buildspec = cls.get_buildspec_for_purge()
        role = cls.deploy_role(name='SpaRoleForCodebuild', session=session)
        cls.deploy_project(name=name,
                           description="This project purges an AWS account of cloud resources",
                           buildspec=buildspec,
                           role=role,
                           session=session)
        cls.build_project(name=name, session=session)
        logging.info("Done")

        # to be moved to the end of the Codebuild buildspec
        Events.emit('PurgedAccount', account)
