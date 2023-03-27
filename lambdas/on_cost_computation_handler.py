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
import logging
import os
import xlsxwriter
from xlsxwriter.utility import xl_rowcol_to_cell

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
    logging.info(f"Computing daily cost metrics per cost center for '{yesterday}'")
    accounts = Settings.scan_settings_for_all_managed_accounts()
    costs = {}
    for account, amount in enumerate_daily_cost_per_account(day=yesterday, session=session):
        logging.info(f"Computing daily costs for account '{account}'")
        cost_center = Account.get_cost_center(tags=accounts.get(str(account), {}).get('tags', {}))
        costs[cost_center] = costs.get(cost_center, 0.0) + float(amount)
    for cost_center in costs.keys():
        logging.info(f"Putting cost as daily metric for cost center '{cost_center}'")
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
    costs = get_amounts_per_cost_center(accounts=accounts, day=last_day_of_previous_month, session=session)
    for cost_center in costs.keys():
        store_report(report=build_detailed_csv_report(cost_center=cost_center, day=last_day_of_previous_month, breakdown=costs[cost_center]),
                     path=get_report_key(label=cost_center, day=last_day_of_previous_month))
        store_report(report=build_detailed_excel_report(cost_center=cost_center, day=last_day_of_previous_month, breakdown=costs[cost_center]),
                     path=get_report_key(label=cost_center, day=last_day_of_previous_month, suffix='xlsx'))
    store_report(report=build_summary_csv_report(costs=costs, day=last_day_of_previous_month),
                 path=get_report_key(label='Summary', day=last_day_of_previous_month))
    store_report(report=build_summary_excel_report(costs=costs, day=last_day_of_previous_month),
                 path=get_report_key(label='Summary', day=last_day_of_previous_month, suffix='xlsx'))
    return '[OK]'


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
        logging.info(f"Processing data for account '{account}'")
        attributes = accounts.get(str(account), {})
        more = dict(name=attributes.get('name', Account.get_name(account)),
                    unit=attributes.get('unit', Account.get_organizational_unit_name(account)))
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


def store_report(path, report):
    logging.info(f"Storing report on S3 bucket on '{path}'")
    boto3.client("s3").put_object(Bucket=os.environ['REPORTS_BUCKET_NAME'],
                                  Key=path,
                                  Body=report)


def build_detailed_csv_report(cost_center, day, breakdown):
    logging.info(f"Building detailed CSV report for cost center '{cost_center}'")
    buffer = io.StringIO()
    writer = DictWriter(buffer,
                        fieldnames=['Cost Center', 'Month', 'Account', 'Name', 'Organizational Unit', 'Service', 'Amount (USD)'])
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
               'Amount (USD)': amount}
        writer.writerow(row)
    row = {'Cost Center': cost_center,
           'Month': day.isoformat()[:7],
           'Account': 'TOTAL',
           'Name': '',
           'Organizational Unit': '',
           'Service': '',
           'Amount (USD)': total}
    writer.writerow(row)
    return buffer.getvalue()


def build_detailed_excel_report(cost_center, day, breakdown):
    logging.info(f"Building detailed Excel report for cost center '{cost_center}'")
    buffer = io.BytesIO()
    workbook = xlsxwriter.Workbook(buffer)
    amount_format = workbook.add_format({'num_format': '# ##0.00'})
    amount_format.set_align('right')
    worksheet = workbook.add_worksheet()
    headers = ['Cost Center', 'Month', 'Account', 'Name', 'Organizational Unit', 'Service', 'Amount (USD)']
    worksheet.write_row(0, 0, headers)
    widths = {index: len(headers[index]) for index in range(len(headers))}
    row = 1
    for item in breakdown:
        data = [str(cost_center),
                day.isoformat()[:7],
                str(item['account']),
                str(item['name']),
                str(item['unit']),
                str(item['service']),
                float(item['amount'])]
        worksheet.write_row(row, 0, data)
        for index in range(len(data)):
            widths[index] = max(widths[index], len(str(data[index])))
        row += 1
    worksheet.write(row, 0, cost_center)
    worksheet.write(row, 1, day.isoformat()[:7])
    worksheet.write(row, 2, 'TOTAL')
    worksheet.write(row, 6, "=SUM(G2:{})".format(xl_rowcol_to_cell(row - 1, 6)))
    for index in range(6):
        worksheet.set_column(index, index, widths[index])
    worksheet.set_column(6, 6, widths[6], amount_format)
    workbook.close()
    return buffer.getvalue()


def build_summary_csv_report(costs, day):
    logging.info("Building summary CSV cost report")
    buffer = io.StringIO()
    writer = DictWriter(buffer,
                        fieldnames=['Cost Center', 'Month', 'Amount (USD)'])
    writer.writeheader()
    summary = 0.0
    for cost_center in costs.keys():
        total = 0.0
        for item in costs[cost_center]:
            total += float(item['amount'])
        summary += total
        row = {'Cost Center': cost_center,
               'Month': day.isoformat()[:7],
               'Amount (USD)': total}
        writer.writerow(row)
    row = {'Cost Center': 'TOTAL',
           'Month': day.isoformat()[:7],
           'Amount (USD)': summary}
    writer.writerow(row)
    return buffer.getvalue()


def build_summary_excel_report(costs, day):
    logging.info("Building summary Excel cost report")
    buffer = io.BytesIO()
    workbook = xlsxwriter.Workbook(buffer)
    amount_format = workbook.add_format({'num_format': '# ##0.00'})
    amount_format.set_align('right')
    worksheet = workbook.add_worksheet()
    headers = ['Cost Center', 'Month', 'Amount (USD)']
    worksheet.write_row(0, 0, headers)
    widths = {index: len(headers[index]) for index in range(len(headers))}
    row = 1
    for cost_center in costs.keys():
        total = 0.0
        for item in costs[cost_center]:
            total += float(item['amount'])
        data = [str(cost_center),
                day.isoformat()[:7],
                float(total)]
        worksheet.write_row(row, 0, data)
        for index in range(len(data)):
            widths[index] = max(widths[index], len(str(data[index])))
        row += 1
    worksheet.write(row, 0, 'TOTAL')
    worksheet.write(row, 1, day.isoformat()[:7])
    worksheet.write(row, 2, "=SUM(C2:{})".format(xl_rowcol_to_cell(row - 1, 2)))
    for index in range(2):
        worksheet.set_column(index, index, widths[index])
    worksheet.set_column(2, 2, widths[2], amount_format)
    workbook.close()
    return buffer.getvalue()


def get_report_key(label, day=None, suffix='csv'):
    day = day or date.today()
    return '/'.join([os.environ["REPORTING_COSTS_PREFIX"],
                     label,
                     f"{day.year:04d}-{day.month:02d}-{label}-costs.{suffix}"])
