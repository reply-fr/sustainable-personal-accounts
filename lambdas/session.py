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

from boto3.session import Session
import botocore
import os
import logging
from uuid import uuid4

cache = None  # session with permissions on top-level account of the organization


def get_organizations_session(session=None):
    ''' get session to top account in the organization '''
    global cache
    if cache:
        return cache
    role = os.environ.get('ROLE_ARN_TO_MANAGE_ACCOUNTS')
    cache = get_assumed_session(role_arn=role, session=session) if role else Session()
    return cache


def get_account_session(account, session=None):
    ''' get session to target account '''
    name = os.environ.get('ROLE_NAME_TO_MANAGE_CODEBUILD', 'AWSControlTowerExecution')
    via = get_organizations_session(session=session)
    target = get_assumed_session(role_arn=f'arn:aws:iam::{account}:role/{name}', session=via)
    identity = target.client('sts').get_caller_identity()
    logging.debug(f"Using identity {identity}")
    return target


def get_assumed_session(role_arn, region=None, name=None, session=None):
    ''' assume a role and derive new session '''
    session = session or Session()
    sts = session.client('sts')

    name = name or 'SPA-{}'.format(uuid4())
    try:
        response = sts.assume_role(RoleArn=role_arn, RoleSessionName=name)
    except botocore.exceptions.ParamValidationError:
        raise ValueError(f"Invalid role ARN '{role_arn}' or name '{name}' for assume role")

    parameters = dict(aws_access_key_id=response['Credentials']['AccessKeyId'],
                      aws_secret_access_key=response['Credentials']['SecretAccessKey'],
                      aws_session_token=response['Credentials']['SessionToken'])
    if region:
        parameters['region_name'] = region

    return Session(**parameters)
