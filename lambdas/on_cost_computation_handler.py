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
from datetime import date, timedelta
import logging
import os

from logger import setup_logging, trap_exception
setup_logging()

from account import Account
from costs import Costs
from events import Events
from metric import put_metric_data
from settings import Settings


@trap_exception
def handle_daily_metric(event=None, context=None, session=None):
    logging.debug(event)
    if event and event.get('date'):
        yesterday = date.fromisoformat(event['date'])
    else:
        yesterday = date.today() - timedelta(days=1)
    logging.info(f"Computing daily cost metrics per cost center for '{yesterday}'")
    accounts = Settings.scan_settings_for_all_managed_accounts()
    costs = {}
    for account, amount in Costs.enumerate_daily_cost_per_account(day=yesterday, session=session):
        logging.info(f"Computing daily costs for account '{account}'")
        cost_center = Account.get_cost_center(tags=accounts.get(str(account), {}).get('tags', {}))
        costs[cost_center] = costs.get(cost_center, 0.0) + float(amount)
    for cost_center in costs.keys():
        logging.info(f"Putting cost as daily metric for cost center '{cost_center}'")
        logging.debug(costs[cost_center])
        put_metric_data(name='DailyCostsByCostCenter',
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
    accounts = Settings.scan_settings_for_all_managed_accounts()
    costs = Costs.get_amounts_per_cost_center(accounts=accounts, day=last_day_of_previous_month, session=session)
    for cost_center in costs.keys():
        store_report(report=Costs.build_detailed_csv_report(cost_center=cost_center, day=last_day_of_previous_month, breakdown=costs[cost_center]),
                     path=get_report_key(label=cost_center, day=last_day_of_previous_month))
        store_report(report=Costs.build_detailed_excel_report(cost_center=cost_center, day=last_day_of_previous_month, breakdown=costs[cost_center]),
                     path=get_report_key(label=cost_center, day=last_day_of_previous_month, suffix='xlsx'))
    store_report(report=Costs.build_summary_csv_report(costs=costs, day=last_day_of_previous_month),
                 path=get_report_key(label='Summary', day=last_day_of_previous_month))
    store_report(report=Costs.build_summary_excel_report(costs=costs, day=last_day_of_previous_month),
                 path=get_report_key(label='Summary', day=last_day_of_previous_month, suffix='xlsx'))
    return '[OK]'


def store_report(path, report):
    logging.info(f"Storing report on S3 bucket on '{path}'")
    boto3.client("s3").put_object(Bucket=os.environ['REPORTS_BUCKET_NAME'],
                                  Key=path,
                                  Body=report)


def get_report_key(label, day=None, suffix='csv'):
    day = day or date.today()
    return '/'.join([os.environ["REPORTING_COSTS_PREFIX"],
                     label,
                     f"{day.year:04d}-{day.month:02d}-{label}-costs.{suffix}"])
