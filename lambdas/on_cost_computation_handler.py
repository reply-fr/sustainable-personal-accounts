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

import boto3
from csv import DictWriter
from datetime import date, timedelta
import io
from itertools import chain
import logging
import os

from logger import setup_logging, trap_exception
setup_logging()

from account import Account
from events import Events
from metric import put_metric_data
from session import get_organizations_session
from settings import Settings


@trap_exception
def handle_daily_metric(event=None, context=None, session=None):
    logging.debug(event)
    if event and event.get('date'):
        yesterday = date.fromisoformat(event['date'])
    else:
        yesterday = date.today() - timedelta(days=1)
    logging.info(f"Computing daily cost metrics per cost center for '{yesterday}")
    accounts = get_accounts_information()
    costs = {}
    for account, amount in enumerate_daily_cost_per_account(day=yesterday, session=session):
        logging.info(f"Computing daily costs for account '{account}")
        cost_center = Account.get_cost_center(tags=accounts.get(str(account), {}).get('tags', {}))
        costs[cost_center] = costs.get(cost_center, 0.0) + float(amount)
    for cost_center in costs.keys():
        logging.info(f"Putting cost as daily metric for cost center '{cost_center}")
        put_metric_data(name='DailyCostByCostCenter',
                        dimensions=[dict(Name='CostCenter', Value=cost_center),
                                    dict(Name='Environment', Value=Events.get_environment())],
                        timestamp=yesterday.isoformat(),
                        value=costs[cost_center],
                        unit='None',
                        session=session)
    return '[OK]'


@trap_exception
def handle_monthly_report(event=None, context=None, session=None):
    logging.debug(event)
    if event and event.get('date'):
        try:
            last_day_of_previous_month = date.fromisoformat(event['date'])
        except ValueError:
            last_day_of_previous_month = date.fromisoformat(event['date'] + '-01')
    else:
        last_day_of_previous_month = date.today().replace(day=1) - timedelta(days=1)
    logging.info(f"Computing cost reports per cost center for month {last_day_of_previous_month.isoformat()[:7]}")
    accounts = get_accounts_information()
    costs = get_amounts_per_cost_center(accounts=accounts, day=last_day_of_previous_month, session=session)
    for cost_center in costs.keys():
        store_report(report=build_detailed_csv_report(cost_center=cost_center, day=last_day_of_previous_month, breakdown=costs[cost_center]),
                     path=get_report_key(label=cost_center, day=last_day_of_previous_month))
    store_report(report=build_summary_csv_report(costs=costs, day=last_day_of_previous_month),
                 path=get_report_key(label='Summary', day=last_day_of_previous_month))
    return '[OK]'


def get_accounts_information():
    logging.debug("Retrieving information for each managed account")
    accounts = {}
    for account in list_all_managed_accounts():
        accounts[account] = Account.describe(account).__dict__
    return accounts


def list_all_managed_accounts(session=None):
    listed_accounts = list_managed_accounts(session=session)
    contained_accounts = enumerate_accounts_in_managed_organizational_units(skip=listed_accounts, session=session)
    return chain(iter(listed_accounts), contained_accounts)


def list_managed_accounts(session=None):
    logging.info("Listing configured accounts")
    return [id for id in Settings.enumerate_accounts(environment=os.environ['ENVIRONMENT_IDENTIFIER'], session=session)]


def enumerate_accounts_in_managed_organizational_units(skip=[], session=None):
    logging.info("Enumerating accounts in configured organizational units")
    for identifier in Settings.enumerate_organizational_units(environment=os.environ['ENVIRONMENT_IDENTIFIER'], session=session):
        logging.info(f"Scanning organizational unit '{identifier}'")
        for account in Account.list(parent=identifier, skip=skip, session=session):
            yield account


def enumerate_daily_cost_per_account(day, session=None):
    logging.info("Fetching daily cost and usage information")
    day = day or date.today()
    start = day - timedelta(days=1)
    end = day
    session = session or get_organizations_session()
    costs = session.client('ce')
    parameters = dict(TimePeriod=dict(Start=start.isoformat()[:10], End=end.isoformat()[:10]),
                      Granularity='DAILY',
                      Metrics=['UnblendedCost'],
                      GroupBy=[dict(Type='DIMENSION', Key='LINKED_ACCOUNT')])
    chunk = costs.get_cost_and_usage(**parameters)
    while chunk.get('ResultsByTime'):
        for result in chunk['ResultsByTime']:
            for group in result['Groups']:
                account = group['Keys'][0]
                amount = group['Metrics']['UnblendedCost']['Amount']
                yield account, amount
        if chunk.get('NextPageToken'):
            chunk = costs.get_cost_and_usage(NextPageToken=chunk.get('NextPageToken'), **parameters)
        else:
            break


def get_amounts_per_cost_center(accounts, day, session):
    costs = {}
    for account, breakdown in enumerate_monthly_breakdown_per_account(day=day, session=session):
        logging.info(f"Processing amounts for account {account}")
        attributes = accounts.get(str(account), {})
        more = dict(name=attributes.get('name', get_account_name(account)),
                    unit=attributes.get('unit', get_account_organizational_unit(account)))
        for item in breakdown:
            item.update(more)
        logging.debug(breakdown)
        cost_center = Account.get_cost_center(tags=attributes.get('tags', {}))
        cumulated = costs.get(cost_center, list())
        cumulated.extend(breakdown)
        costs[cost_center] = cumulated
    return costs


def enumerate_monthly_breakdown_per_account(day=None, session=None):
    logging.info("Fetching monthly cost and usage information")
    day = day or date.today()
    start = day.replace(day=1)
    end = (start + timedelta(days=32)).replace(day=1)
    session = session or get_organizations_session()
    costs = session.client('ce')
    parameters = dict(TimePeriod=dict(Start=start.isoformat()[:10], End=end.isoformat()[:10]),
                      Granularity='MONTHLY',
                      Metrics=['UnblendedCost'],
                      GroupBy=[dict(Type='DIMENSION', Key='LINKED_ACCOUNT'),
                               dict(Type='DIMENSION', Key='SERVICE')])
    chunk = costs.get_cost_and_usage(**parameters)
    breakdowns_per_account = {}
    while chunk.get('ResultsByTime'):
        for result in chunk['ResultsByTime']:
            for group in result['Groups']:
                account = group['Keys'][0]
                service = group['Keys'][1]
                amount = group['Metrics']['UnblendedCost']['Amount']
                cumulated = breakdowns_per_account.get(account, [])
                cumulated.append(dict(account=account, service=service, amount=amount))
                breakdowns_per_account[account] = cumulated
        if chunk.get('NextPageToken'):
            chunk = costs.get_cost_and_usage(NextPageToken=chunk.get('NextPageToken'), **parameters)
        else:
            break
    for account, breakdown in breakdowns_per_account.items():
        yield account, breakdown


def get_account_name(account, session=None):
    session = session or get_organizations_session()
    return session.client('organizations').describe_account(AccountId=account)['Account']['Name']


def get_account_organizational_unit(account, session=None):
    session = session or get_organizations_session()
    response = session.client('organizations').list_parents(ChildId=account)
    if 'Parents' in response.keys():
        return response['Parents'][0]['Id']
    else:
        return ''


def store_report(path, report):
    logging.info(f"Storing report on S3 bucket on '{path}'")
    headings = (report + "\n\n\n").split('\n')[:3]
    logging.debug(f"{headings[0]}\n{headings[1]}\n{headings[2]}\n...")
    boto3.client("s3").put_object(Bucket=os.environ['REPORTS_BUCKET_NAME'],
                                  Key=path,
                                  Body=report)


def build_detailed_csv_report(cost_center, day, breakdown):
    logging.info(f"Building detailed CSV report for cost center '{cost_center}'")
    buffer = io.StringIO()
    writer = DictWriter(buffer,
                        fieldnames=['Cost Center', 'Month', 'Account', 'Name', 'Organizational Unit', 'Service', 'Amount (USD)'],
                        delimiter='\t')
    writer.writeheader()
    total = 0.0
    for item in breakdown:
        amount = float(item['amount'])
        total += amount
        row = {'Cost Center': cost_center,
               'Month': day.isoformat()[:7],
               'Account': item['account'],
               'Name': item.get('name', ''),
               'Organizational Unit': item.get('unit', ''),
               'Service': item['service'],
               'Amount (USD)': make_float(amount)}
        writer.writerow(row)
    row = {'Cost Center': cost_center,
           'Month': day.isoformat()[:7],
           'Account': 'TOTAL',
           'Name': '',
           'Organizational Unit': '',
           'Service': '',
           'Amount (USD)': make_float(total)}
    writer.writerow(row)
    return buffer.getvalue()


def build_summary_csv_report(costs, day):
    logging.info("Building summary CSV cost report")
    buffer = io.StringIO()
    writer = DictWriter(buffer,
                        fieldnames=['Cost Center', 'Month', 'Amount (USD)'],
                        delimiter='\t')
    writer.writeheader()
    summary = 0.0
    for cost_center in costs.keys():
        total = 0.0
        for item in costs[cost_center]:
            total += float(item['amount'])
        summary += total
        row = {'Cost Center': cost_center,
               'Month': day.isoformat()[:7],
               'Amount (USD)': make_float(total)}
        writer.writerow(row)
    row = {'Cost Center': 'TOTAL',
           'Month': day.isoformat()[:7],
           'Amount (USD)': make_float(summary)}
    writer.writerow(row)
    return buffer.getvalue()


def make_float(number):
    return str(number)


def get_report_key(label, day=None):
    day = day or date.today()
    return '/'.join([os.environ["REPORTING_COSTS_PREFIX"],
                     label,
                     f"{day.year:04d}-{day.month:02d}-{label}-costs.csv"])
