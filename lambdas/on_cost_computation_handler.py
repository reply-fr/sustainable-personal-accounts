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
from markdown import markdown
import os

from logger import setup_logging, trap_exception
setup_logging()

from account import Account
from costs import Costs
from e_mail import Email
from events import Events
from metric import put_metric_data
from settings import Settings


@trap_exception
def handle_daily_metrics(event=None, context=None, session=None):
    logging.debug(event)
    if event and event.get('date'):
        yesterday = date.fromisoformat(event['date'])
    else:
        yesterday = date.today() - timedelta(days=1)
    logging.info(f"Computing daily cost metrics per cost center for '{yesterday}'")
    accounts = Settings.scan_settings_for_all_managed_accounts()
    costs = {}
    for account, amount in Costs.enumerate_daily_costs_per_account(day=yesterday, session=session):
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
def handle_monthly_reports(event=None, context=None, session=None):
    logging.debug(event)
    if event and event.get('date'):
        try:
            last_day_of_previous_month = date.fromisoformat(event['date'])
        except ValueError:
            last_day_of_previous_month = date.fromisoformat(event['date'] + '-01')
    else:
        last_day_of_previous_month = date.today().replace(day=1) - timedelta(days=1)
    accounts = Settings.scan_settings_for_all_managed_accounts()

    build_charge_reports_per_cost_center(accounts=accounts, day=last_day_of_previous_month, session=session)
    build_service_reports_per_cost_center(accounts=accounts, day=last_day_of_previous_month, session=session)


def build_charge_reports_per_cost_center(accounts, day, session):
    logging.info(f"Computing charge reports per cost center for month {day.isoformat()[:7]}")
    charges = Costs.get_charges_per_cost_center(accounts=accounts, day=day, session=session)

    path_of_xlsx = get_report_path(cost_center='Summary', label='charges', day=day, suffix='xlsx')
    store_report(report=Costs.build_summary_of_charges_excel_report(charges=charges, day=day), path=path_of_xlsx)

    path_of_csv = get_report_path(cost_center='Summary', label='charges', day=day, suffix='csv')
    store_report(report=Costs.build_summary_of_charges_csv_report(charges=charges, day=day), path=path_of_csv)

    email_reports(day=day, objects=[f"s3://{os.environ['REPORTS_BUCKET_NAME']}/{path_of_xlsx}",
                                    f"s3://{os.environ['REPORTS_BUCKET_NAME']}/{path_of_csv}"])
    return '[OK]'


def build_service_reports_per_cost_center(accounts, day, session):
    logging.info(f"Computing service reports per cost center for month {day.isoformat()[:7]}")
    services = Costs.get_services_per_cost_center(accounts=accounts, day=day, session=session)
    for cost_center in services.keys():
        store_report(report=Costs.build_breakdown_of_services_csv_report_for_cost_center(cost_center=cost_center, day=day, breakdown=services[cost_center]),
                     path=get_report_path(cost_center=cost_center, label='services', day=day))
        store_report(report=Costs.build_breakdown_of_services_excel_report_for_cost_center(cost_center=cost_center, day=day, breakdown=services[cost_center]),
                     path=get_report_path(cost_center=cost_center, label='services', day=day, suffix='xlsx'))

    store_report(report=Costs.build_summary_of_services_csv_report(costs=services, day=day),
                 path=get_report_path(cost_center='Summary', label='services', day=day))
    path = get_report_path(cost_center='Summary', label='services', day=day, suffix='xlsx')
    store_report(report=Costs.build_summary_of_services_excel_report(costs=services, day=day), path=path)


def email_reports(day, objects):
    sender = os.environ.get('ORIGIN_EMAIL_RECIPIENT')
    if not sender:
        logging.debug("Skipping the sending of cost report; Set 'with_origin_email_recipient' attribute to activate the feature")
        return
    recipients = os.environ.get('COST_EMAIL_RECIPIENTS')
    if not recipients:
        logging.debug("Skipping the sending of cost report; Set 'with_cost_email_recipients' attribute with list of report recipients")
        return

    subject = f"Summary cost report for {day.year:04d}-{day.month:02d}"
    simple = f"You will find attached cloud cost reports for {day.year:04d}-{day.month:02d}"
    template = os.environ.get('REPORTING_COSTS_MARKDOWN') or "You will find attached cloud cost reports for {month}"
    complex = template.format(month=f"{day.year:04d}-{day.month:02d}")
    return Email.send_objects(sender=sender, recipients=recipients, subject=subject, text=simple, html=markdown(complex), objects=objects)


def get_report_path(cost_center, label, day=None, suffix='csv'):
    day = day or date.today()
    return '/'.join([os.environ["REPORTING_COSTS_PREFIX"],
                     cost_center,
                     f"{day.year:04d}-{day.month:02d}-{cost_center}-{label}.{suffix}"])


def store_report(path, report):
    logging.info(f"Storing report on S3 bucket on '{path}'")
    boto3.client("s3").put_object(Bucket=os.environ['REPORTS_BUCKET_NAME'],
                                  Key=path,
                                  Body=report)
