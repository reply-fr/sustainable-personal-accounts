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

from base64 import b64encode
import boto3
from boto3.session import Session
import botocore
from datetime import date
import json
import logging
import os

from logger import setup_logging, trap_exception
setup_logging()

from account import Account
from costs import Costs
from events import Events
from metric import put_metric_data


SUMMARY_TEMPLATE = "# {}\n\n{}"  # markdown is supported


@trap_exception
def handle_exception(event, context=None, session=None):
    logging.debug(event)
    input = Events.decode_spa_event(event)
    incident_arn = start_incident(label=input.label, payload=input.payload, session=session)
    tag_incident(incident_arn=incident_arn, payload=input.payload, session=session)
    attach_cost_report(incident_arn=incident_arn, payload=input.payload, session=session)
    put_metric_data(name='ExceptionsByLabel',
                    dimensions=[dict(Name='Label', Value=input.label),
                                dict(Name='Environment', Value=Events.get_environment())],
                    session=session)
    return f"[OK] {input.label}"


@trap_exception
def handle_attachment_request(event, context=None):  # web proxy to attachments on s3 bucket
    logging.debug(event)
    return download_attachment(path=event.get('rawPath', '/'), headers=event.get('headers', {}))


def start_incident(label, payload, session=None):
    logging.info(f"Starting incident '{payload}'")
    title = payload.get('title', '*no title*')
    session = session or Session()
    incidents = session.client('ssm-incidents')
    response = incidents.start_incident(title=title,
                                        impact=int(payload.get('impact', 4)),
                                        responsePlanArn=os.environ['RESPONSE_PLAN_ARN'])
    summary = SUMMARY_TEMPLATE.format(title, payload.get('message', '*no message*')).replace('\n', '  \n')  # force newlines in markdown
    incidents.update_incident_record(arn=response['incidentRecordArn'], summary=summary)
    incidents.tag_resource(resourceArn=response['incidentRecordArn'], tags={'exception': label})
    logging.debug("Done")
    return response['incidentRecordArn']


def tag_incident(incident_arn, payload, session=None):
    account = payload.get('account', '123456789012')
    if not account:
        logging.debug(f"No account identifier in {payload}")
        return

    logging.info("Tagging incident report with account information")
    try:
        session = session or Session()
        incidents = session.client('ssm-incidents')
        attributes = Account.describe(id=account)
        incidents.tag_resource(resourceArn=incident_arn,
                               tags={'account': account,
                                     'account-email': attributes.email,
                                     'account-name': attributes.name,
                                     'cost-center': Account.get_cost_center(attributes.tags),
                                     'organizational-unit': attributes.unit})
        logging.debug("Done")
    except botocore.exceptions.ClientError as exception:
        logging.error(exception)


def attach_cost_report(incident_arn, payload, session=None, day=None):
    day = day or date.today()
    account = payload.get('account')
    if not account:
        logging.debug(f"No account identifier in {payload}")
        return

    logging.info("Attaching cost and usage report to incident report")
    try:
        breakdown = Costs.enumerate_monthly_breakdown_for_account(account=account, day=day, session=session)
        path = get_report_path(label=str(account), day=day)
        store_report(path=path, report=Costs.build_excel_report_for_account(account=account, day=day, breakdown=breakdown))
        add_related_item(incident_arn=incident_arn,
                         title='Cost and Usage Report',
                         url=get_report_url(path=path),
                         session=session)
        logging.debug("Done")
    except botocore.exceptions.ClientError as exception:
        logging.error(exception)


def get_report_path(label, day=None):
    day = day or date.today()
    return '/'.join([os.environ["REPORTING_EXCEPTIONS_PREFIX"],
                     label,
                     f"{day.year:04d}-{day.month:02d}-{label}-cost-and-usage.xlsx"])


def store_report(path, report):
    logging.info("Storing report on S3 bucket...")
    logging.debug(report)
    boto3.client("s3").put_object(Bucket=os.environ['REPORTS_BUCKET_NAME'],
                                  Key=path,
                                  Body=report)


def add_related_item(incident_arn, title, url, session):
    logging.info(f"Attaching URL '{url}' to incident record...")
    session = session or Session()
    im = session.client('ssm-incidents')
    im.update_related_items(
        incidentRecordArn=incident_arn,
        relatedItemsUpdate=dict(itemToAdd={'identifier': dict(type='ATTACHMENT', value=dict(url=url)),
                                           'title': title}))


def get_report_url(path):
    web_endpoint = get_download_attachment_web_endpoint()
    prefix = os.environ["REPORTING_EXCEPTIONS_PREFIX"] + '/'
    if path.startswith(prefix):
        path = path[len(prefix):]
    return '/'.join([web_endpoint.rstrip('/'), path])


def get_download_attachment_web_endpoint():
    ssm = boto3.client('ssm')
    item = ssm.get_parameter(Name=os.environ['WEB_ENDPOINTS_PARAMETER'])
    web_endpoints = json.loads(item['Parameter']['Value'])
    return web_endpoints["OnException.DownloadAttachment.WebEndpoint"]


def download_attachment(path, headers={}):

    # enforce navigation from aws console -- https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Sec-Fetch-Mode
    # required = {('sec-fetch-mode', 'navigate'), ('sec-fetch-site', 'cross-site'), ('sec-fetch-user', '?1'), ('sec-fetch-dest', 'document')}
    # for key, expected in required:
    #     if headers.get(key) != expected:
    #         logging.warning(f"403 - Missing header: '{key}': '{expected}'")
    #         return dict(statusCode=403,
    #                     headers={'Content-Type': 'application/json'},
    #                     body=json.dumps({'error': "You are not allowed to fetch this document"}))

    if ('..' in path) or ('?' in path):
        logging.warning("400 - Dangerous link detected. We do not handle this request.")
        return dict(statusCode=400,
                    headers={'Content-Type': 'application/json'},
                    body=json.dumps({'error': "Invalid path has been requested"}))
    bucket = os.environ['REPORTS_BUCKET_NAME']
    path = '/'.join([os.environ["REPORTING_EXCEPTIONS_PREFIX"], path.lstrip('/')])
    logging.info(f"Looking for object key '{path}' in bucket '{bucket}'")
    s3 = boto3.client('s3')
    try:
        response = s3.get_object(Bucket=bucket, Key=path)
        file_name = os.path.basename(path)
        body = b64encode(response['Body'].read()).decode()
        logging.debug(f"Transmitting {len(body)} bytes")
        return dict(statusCode=200,
                    headers={'Content-Type': 'application/octet-stream',
                             'Content-Disposition': f'attachment; filename="{file_name}"'},  # force download
                    body=body,
                    isBase64Encoded=True)
    except s3.exceptions.NoSuchKey:
        logging.warning("404 - Not Found")
        return dict(statusCode=404,
                    headers={'Content-Type': 'application/json'},
                    body=json.dumps({'error': 'Unable to find the requested object'}))
    except Exception as exception:
        logging.error(f"500 - Internal Error - {str(exception)}")
        return dict(statusCode=500,
                    headers={'Content-Type': 'application/json'},
                    body=json.dumps({'error': str(exception)}))
