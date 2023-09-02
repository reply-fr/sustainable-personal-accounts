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
import os


def lambda_handler(event, context):
    print("Handling CodeCommit state change")
    print(event)
    start_codebuild_project(session=get_assumed_session())


def start_codebuild_project(session):
    name = os.environ.get('NAME_OF_PROJECT_TO_START')
    session.client('codebuild').start_build(projectName=name)
    print(f"CodeBuild project '{name}' has been started")


def get_assumed_session():
    role_arn = os.environ.get('ARN_OF_ROLE_TO_ASSUME')
    name = 'SPA-Triggering'
    response = Session().client('sts').assume_role(RoleArn=role_arn, RoleSessionName=name)
    print(f"IAM role '{role_arn}' has been assumed")

    parameters = dict(aws_access_key_id=response['Credentials']['AccessKeyId'],
                      aws_secret_access_key=response['Credentials']['SecretAccessKey'],
                      aws_session_token=response['Credentials']['SessionToken'])
    return Session(**parameters)
