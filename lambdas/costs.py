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

from csv import DictWriter
from datetime import date, timedelta
import io
import logging
import xlsxwriter
from xlsxwriter.utility import xl_rowcol_to_cell

from account import Account
from session import get_account_session, get_organizations_session


class Costs:

    COSTLY_RECORDS = ['Usage', 'Upfront', 'Recurring', 'Support', 'Tax', 'Other']

    @classmethod
    def enumerate_daily_cost_per_account(cls, day=None, session=None):
        logging.info("Fetching daily cost and usage information per account")
        day = day or date.today()
        start = day - timedelta(days=1)
        end = day
        session = session or get_organizations_session()
        costs = session.client('ce')
        parameters = dict(TimePeriod=dict(Start=start.isoformat()[:10], End=end.isoformat()[:10]),
                          Granularity='DAILY',
                          Metrics=['UnblendedCost'],
                          Filter=dict(Dimensions=dict(Key='RECORD_TYPE', Values=cls.COSTLY_RECORDS)),
                          GroupBy=[dict(Type='DIMENSION', Key='LINKED_ACCOUNT')])
        chunk = costs.get_cost_and_usage(**parameters)
        logging.debug(chunk)
        while chunk.get('ResultsByTime'):
            for result in chunk['ResultsByTime']:
                for group in result['Groups']:
                    account = group['Keys'][0]
                    amount = group['Metrics']['UnblendedCost']['Amount']
                    yield account, amount
            if chunk.get('NextPageToken'):
                chunk = costs.get_cost_and_usage(NextPageToken=chunk.get('NextPageToken'), **parameters)
                logging.debug(chunk)
            else:
                break

    @classmethod
    def enumerate_monthly_breakdown_per_account(cls, day=None, session=None):
        logging.info("Fetching monthly cost and usage information per account")
        day = day or date.today()
        start = day.replace(day=1)                         # first day of this month is included
        end = (start + timedelta(days=32)).replace(day=1)  # first day of next month is excluded
        session = session or get_organizations_session()
        costs = session.client('ce')
        parameters = dict(TimePeriod=dict(Start=start.isoformat()[:10], End=end.isoformat()[:10]),
                          Granularity='MONTHLY',
                          Metrics=['UnblendedCost'],
                          Filter=dict(Dimensions=dict(Key='RECORD_TYPE', Values=cls.COSTLY_RECORDS)),
                          GroupBy=[dict(Type='DIMENSION', Key='LINKED_ACCOUNT'),
                                   dict(Type='DIMENSION', Key='SERVICE')])
        chunk = costs.get_cost_and_usage(**parameters)
        logging.debug(chunk)
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
                logging.debug(chunk)
            else:
                break
        for account, breakdown in breakdowns_per_account.items():
            yield account, breakdown

    @classmethod
    def enumerate_monthly_breakdown_for_account(cls, account, day=None, session=None):
        logging.info(f"Fetching monthly cost and usage information for account '{account}'...")
        day = day or date.today()
        session = session or get_account_session(account=account)
        costs = session.client('ce')
        parameters = dict(TimePeriod=dict(Start=day.replace(day=1).isoformat()[:10], End=day.isoformat()[:10]),
                          Granularity='MONTHLY',
                          Metrics=['UnblendedCost'],
                          Filter=dict(And=[dict(Dimensions=dict(Key='LINKED_ACCOUNT', Values=[account])),
                                           dict(Dimensions=dict(Key='RECORD_TYPE', Values=cls.COSTLY_RECORDS))]),
                          GroupBy=[dict(Type='DIMENSION', Key='SERVICE')])
        chunk = costs.get_cost_and_usage(**parameters)
        logging.debug(chunk)
        while chunk.get('ResultsByTime'):
            for result in chunk['ResultsByTime']:
                for group in result['Groups']:
                    yield {'start': result['TimePeriod']['Start'],
                           'end': result['TimePeriod']['End'],
                           'service': group['Keys'][0],
                           'amount': group['Metrics']['UnblendedCost']['Amount']}
            if chunk.get('NextPageToken'):
                chunk = costs.get_cost_and_usage(NextPageToken=chunk.get('NextPageToken'), **parameters)
                logging.debug(chunk)
            else:
                break

    @classmethod
    def enumerate_monthly_charges_per_account(cls, day=None, session=None):
        logging.info("Fetching monthly cost and charges information per account")
        day = day or date.today()
        start = day.replace(day=1)                         # first day of this month is included
        end = (start + timedelta(days=32)).replace(day=1)  # first day of next month is excluded
        session = session or get_organizations_session()
        costs = session.client('ce')
        parameters = dict(TimePeriod=dict(Start=start.isoformat()[:10], End=end.isoformat()[:10]),
                          Granularity='MONTHLY',
                          Metrics=['UnblendedCost'],
                          GroupBy=[dict(Type='DIMENSION', Key='LINKED_ACCOUNT'),
                                   dict(Type='DIMENSION', Key='RECORD_TYPE')])
        chunk = costs.get_cost_and_usage(**parameters)
        logging.debug(chunk)
        charges_per_account = {}
        while chunk.get('ResultsByTime'):
            for result in chunk['ResultsByTime']:
                for group in result['Groups']:
                    account = group['Keys'][0]
                    charge = group['Keys'][1]
                    amount = group['Metrics']['UnblendedCost']['Amount']
                    cumulated = charges_per_account.get(account, [])
                    cumulated.append(dict(account=account, charge=charge, amount=amount))
                    charges_per_account[account] = cumulated
            if chunk.get('NextPageToken'):
                chunk = costs.get_cost_and_usage(NextPageToken=chunk.get('NextPageToken'), **parameters)
                logging.debug(chunk)
            else:
                break
        for account, charges in charges_per_account.items():
            yield account, charges

    @classmethod
    def get_breakdowns_per_cost_center(cls, accounts, day=None, session=None):
        costs = {}
        for account, breakdown in cls.enumerate_monthly_breakdown_per_account(day=day, session=session):
            logging.debug(f"Processing services for account '{account}'")
            attributes = accounts.get(str(account), {})
            more = dict(name=attributes.get('name') or Account.get_name(account),
                        unit=attributes.get('unit_name') or Account.get_organizational_unit_name(account))
            for item in breakdown:
                item.update(more)
            logging.debug(breakdown)
            cost_center = Account.get_cost_center(tags=attributes.get('tags', {}))
            cumulated = costs.get(cost_center, [])
            cumulated.extend(breakdown)
            costs[cost_center] = cumulated
        return costs

    @classmethod
    def get_charges_per_cost_center(cls, accounts, day=None, session=None):
        costs = {}
        for account, charges in cls.enumerate_monthly_charges_per_account(day=day, session=session):
            logging.debug(f"Processing charges for account '{account}'")
            attributes = accounts.get(str(account), {})
            more = dict(name=attributes.get('name') or Account.get_name(account),
                        unit=attributes.get('unit_name') or Account.get_organizational_unit_name(account))
            for item in charges:
                item.update(more)
            logging.debug(charges)
            attributes = accounts.get(str(account), {})
            cost_center = Account.get_cost_center(tags=attributes.get('tags', {}))
            cumulated = costs.get(cost_center, [])
            cumulated.extend(charges)
            costs[cost_center] = cumulated
        return costs

    @classmethod
    def build_breakdown_csv_report_for_cost_center(cls, cost_center, day, breakdown):
        logging.info(f"Building breakdown CSV report for cost center '{cost_center}'")
        buffer = io.StringIO()
        writer = DictWriter(buffer, fieldnames=['Cost Center', 'Month', 'Organizational Unit', 'Account', 'Name', 'Service', 'Amount (USD)'])
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

    @classmethod
    def build_breakdown_csv_report(cls, costs, day):
        logging.info("Building summary CSV report")
        buffer = io.StringIO()
        writer = DictWriter(buffer, fieldnames=['Cost Center', 'Month', 'Organizational Unit', 'Amount (USD)'])
        writer.writeheader()
        summary = 0.0
        for cost_center in costs.keys():
            units = {}
            total = 0.0
            for item in costs[cost_center]:
                amount = float(item['amount'])
                name = item['unit']
                value = units.get(name, 0.0)
                units[name] = value + amount
                total += amount
            summary += total
            for name in units.keys():
                row = {'Cost Center': cost_center,
                       'Month': day.isoformat()[:7],
                       'Organizational Unit': name,
                       'Amount (USD)': units[name]}
                writer.writerow(row)
            row = {'Cost Center': cost_center,
                   'Month': day.isoformat()[:7],
                   'Organizational Unit': '',
                   'Amount (USD)': total}
            writer.writerow(row)
        row = {'Cost Center': 'TOTAL',
               'Month': day.isoformat()[:7],
               'Organizational Unit': '',
               'Amount (USD)': summary}
        writer.writerow(row)
        return buffer.getvalue()

    @classmethod
    def build_excel_report_for_account(cls, account, day, breakdown):
        logging.info(f"Building Excel report for account '{account}'")
        buffer = io.BytesIO()
        workbook = xlsxwriter.Workbook(buffer)
        amount_format = workbook.add_format({'num_format': '# ##0.00'})
        amount_format.set_align('right')
        worksheet = workbook.add_worksheet()
        headers = ['Account', 'Month', 'Service', 'Amount (USD)']
        worksheet.write_row(0, 0, headers)
        widths = {index: len(headers[index]) for index in range(len(headers))}
        row = 1
        for item in breakdown:
            data = [str(account),
                    day.isoformat()[:7],
                    str(item['service']),
                    float(item['amount'])]
            worksheet.write_row(row, 0, data)
            for index in range(len(data)):
                widths[index] = max(widths[index], len(str(data[index])))
            row += 1
        worksheet.write(row, 0, str(account))
        worksheet.write(row, 1, day.isoformat()[:7])
        worksheet.write(row, 2, 'TOTAL')
        worksheet.write(row, 3, "=SUM(D2:{})".format(xl_rowcol_to_cell(row - 1, 3)))
        for index in range(4):
            worksheet.set_column(index, index, widths[index])
        worksheet.set_column(3, 3, widths[3], amount_format)
        workbook.close()
        return buffer.getvalue()

    @classmethod
    def build_breakdown_excel_report_for_cost_center(cls, cost_center, day, breakdown):
        logging.info(f"Building detailed Excel report for cost center '{cost_center}'")
        buffer = io.BytesIO()
        workbook = xlsxwriter.Workbook(buffer)
        amount_format = workbook.add_format({'num_format': '# ##0.00'})
        amount_format.set_align('right')
        worksheet = workbook.add_worksheet()
        headers = ['Cost Center', 'Month', 'Organizational Unit', 'Account', 'Name', 'Service', 'Amount (USD)']
        worksheet.write_row(0, 0, headers)
        widths = {index: len(headers[index]) for index in range(len(headers))}
        row = 1
        for item in breakdown:
            data = [str(cost_center),
                    day.isoformat()[:7],
                    str(item['unit']),
                    str(item['account']),
                    str(item['name']),
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

    @classmethod
    def build_breakdown_excel_report(cls, costs, day):
        logging.info("Building summary Excel cost report")
        buffer = io.BytesIO()
        workbook = xlsxwriter.Workbook(buffer)
        amount_format = workbook.add_format({'num_format': '# ##0.00'})
        amount_format.set_align('right')
        worksheet = workbook.add_worksheet()
        headers = ['Cost Center', 'Month', 'Organizational Unit', 'Amount (USD)']
        worksheet.write_row(0, 0, headers)
        widths = {index: len(headers[index]) for index in range(len(headers))}
        subs = []
        row = 1
        month = day.isoformat()[:7]
        for cost_center in costs.keys():
            head = row
            units = {}
            for item in costs[cost_center]:
                amount = float(item['amount'])
                name = item['unit']
                value = units.get(name, 0.0)
                units[name] = value + amount
            for name in units.keys():
                data = [str(cost_center), month, name, units[name]]
                worksheet.write_row(row, 0, data)
                worksheet.set_row(row, None, None, {'level': 2, 'hidden': True})
                row += 1
            data = [str(cost_center),
                    month,
                    '',
                    f"=SUM({xl_rowcol_to_cell(head, 3)}:{xl_rowcol_to_cell(row - 1, 3)})"]
            worksheet.write_row(row, 0, data)
            worksheet.set_row(row, None, None, {'level': 1, 'collapsed': True})
            subs.append(xl_rowcol_to_cell(row, 3))
            row += 1
            for index in range(len(data)):
                widths[index] = max(widths[index], len(str(data[index])))
        worksheet.write(row, 0, 'TOTAL')
        worksheet.write(row, 1, month)
        worksheet.write(row, 3, '=' + '+'.join(subs))
        for index in range(3):
            worksheet.set_column(index, index, widths[index])
        worksheet.set_column(3, 3, widths[2], amount_format)
        workbook.close()
        return buffer.getvalue()

    @classmethod
    def build_summary_of_charges_csv_report(cls, charges, day):
        logging.info("Building CSV report: summary of charges")
        buffer = io.StringIO()
        types = set()
        for cost_center in charges.keys():
            types = types.union(set(item['charge'] for item in charges[cost_center]))
        labels = {k: f"{k} (USD)" for k in types}
        headers = ['Cost Center', 'Month', 'Organizational Unit', 'Charges (USD)']
        headers.extend(sorted(list(labels.values())))
        logging.debug(headers)
        writer = DictWriter(buffer, fieldnames=headers)
        writer.writeheader()
        for cost_center in charges.keys():
            units = {}
            for item in charges[cost_center]:
                amount = float(item['amount'])
                unit = item['unit']
                values = units.get(unit, {})
                charge = item['charge']
                values[charge] = values.get(charge, 0.0) + amount
                values['total'] = values.get('total', 0.0) + amount
                units[unit] = values
            for name in units.keys():
                values = units[name]
                row = {'Cost Center': cost_center,
                       'Month': day.isoformat()[:7],
                       'Organizational Unit': name,
                       'Charges (USD)': values['total']}
                for key, header in labels.items():
                    row[header] = values.get(key, 0.0)
                logging.debug(row)
                writer.writerow(row)
        return buffer.getvalue()

    @classmethod
    def build_summary_of_charges_excel_report(cls, charges, day):
        logging.info("Building Excel report: summary of charges")
        buffer = io.BytesIO()
        workbook = xlsxwriter.Workbook(buffer)
        worksheet = workbook.add_worksheet()
        types = set()
        for cost_center in charges.keys():
            types = types.union(set(item['charge'] for item in charges[cost_center]))
        labels = sorted(types)
        headers = ['Cost Center', 'Month', 'Organizational Unit', 'Charges (USD)']
        headers.extend([f"{label} (USD)" for label in labels])
        logging.debug(headers)
        worksheet.write_row(0, 0, headers)
        widths = {index: len(headers[index]) for index in range(len(headers))}
        subs = []
        row = 1
        month = day.isoformat()[:7]
        for cost_center in charges.keys():
            head = row
            units = {}
            for item in charges[cost_center]:
                amount = float(item['amount'])
                unit = item['unit']
                values = units.get(unit, {})
                charge = item['charge']
                values[charge] = values.get(charge, 0.0) + amount
                values['total'] = values.get('total', 0.0) + amount
                units[unit] = values
            for name, values in units.items():
                data = [str(cost_center), month, name]
                data.append(values['total'])
                for key in labels:
                    data.append(values.get(key, 0.0))
                logging.debug(data)
                worksheet.write_row(row, 0, data)
                worksheet.set_row(row, None, None, {'level': 2, 'hidden': True})
                row += 1
            data = [str(cost_center), month, '']
            for delta in range(1 + len(labels)):
                data.append(f"=SUM({xl_rowcol_to_cell(head, 3 + delta)}:{xl_rowcol_to_cell(row - 1, 3 + delta)})")
            logging.debug(data)
            worksheet.write_row(row, 0, data)
            worksheet.set_row(row, None, None, {'level': 1, 'collapsed': True})
            subs.append([xl_rowcol_to_cell(row, 3 + delta) for delta in range(1 + len(labels))])
            for index in range(len(data)):
                widths[index] = max(widths[index], len(str(data[index])))
            row += 1
        cls.add_total_row(worksheet=worksheet, row=row, month=month, subs=subs)
        cls.set_columns(workbook=workbook, worksheet=worksheet, widths=widths)
        workbook.close()
        return buffer.getvalue()

    @classmethod
    def add_total_row(cls, worksheet, row, month, subs):
        data = ['TOTAL', month, '']
        columns = len(subs[0])
        verticals = []
        for delta in range(columns):
            verticals.append([])
        for cumulated in subs:
            for delta in range(columns):
                verticals[delta].append(cumulated[delta])
        for vertical in verticals:
            data.append('=' + '+'.join(vertical))
        logging.debug(data)
        worksheet.write_row(row, 0, data)

    @classmethod
    def set_columns(cls, workbook, worksheet, widths):
        amount_format = workbook.add_format({'num_format': '# ##0.00'})
        amount_format.set_align('right')
        for index in range(len(widths)):
            if index > 2:
                worksheet.set_column(index, index, widths[index], amount_format)
            else:
                worksheet.set_column(index, index, widths[index])
