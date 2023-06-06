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
    def enumerate_daily_costs_per_account(cls, day=None, session=None):
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
    def enumerate_monthly_costs_for_account(cls, account, day=None, session=None):
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
    def enumerate_monthly_services_per_account(cls, day=None, session=None):
        logging.info("Fetching monthly cost and service information per account")
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
    def get_services_per_cost_center(cls, accounts, day=None, session=None):
        costs = {}
        for account, breakdown in cls.enumerate_monthly_services_per_account(day=day, session=session):
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
    def build_breakdown_of_costs_excel_report_for_account(cls, account, day, breakdown):
        logging.info(f"Building Excel report for account '{account}'")
        buffer = io.BytesIO()
        workbook = xlsxwriter.Workbook(buffer)
        amount_format = workbook.add_format({'num_format': '# ##0.00'})
        amount_format.set_align('right')
        worksheet = workbook.add_worksheet()
        headers = ['Month', 'Account', 'Service', 'Amount (USD)']
        worksheet.write_row(0, 0, headers)
        widths = {index: len(headers[index]) for index in range(len(headers))}
        row = 1
        for item in breakdown:
            data = [day.isoformat()[:7],
                    str(account),
                    str(item['service']),
                    float(item['amount'])]
            worksheet.write_row(row, 0, data)
            for index in range(len(data)):
                widths[index] = max(widths[index], len(str(data[index])))
            row += 1
        worksheet.write(row, 0, day.isoformat()[:7])
        worksheet.write(row, 1, str(account))
        worksheet.write(row, 2, 'TOTAL')
        worksheet.write(row, 3, "=SUM(D2:{})".format(xl_rowcol_to_cell(row - 1, 3)))
        for index in range(4):
            worksheet.set_column(index, index, widths[index])
        worksheet.set_column(3, 3, widths[3], amount_format)
        workbook.close()
        return buffer.getvalue()

    @classmethod
    def build_breakdown_of_services_csv_report_for_cost_center(cls, cost_center, day, breakdown):
        logging.info(f"Building CSV report: breakdown of services for cost center '{cost_center}'")
        buffer = io.StringIO()
        writer = DictWriter(buffer, fieldnames=['Month', 'Cost Center', 'Organizational Unit', 'Account', 'Name', 'Service', 'Amount (USD)'])
        writer.writeheader()
        total = 0.0
        for item in breakdown:
            amount = float(item['amount'])
            total += amount
            row = {'Month': day.isoformat()[:7],
                   'Cost Center': cost_center,
                   'Account': item['account'],
                   'Name': item.get('name', ''),
                   'Organizational Unit': item.get('unit', ''),
                   'Service': item['service'],
                   'Amount (USD)': amount}
            writer.writerow(row)
        row = {'Month': day.isoformat()[:7],
               'Cost Center': cost_center,
               'Account': 'TOTAL',
               'Name': '',
               'Organizational Unit': '',
               'Service': '',
               'Amount (USD)': total}
        writer.writerow(row)
        return buffer.getvalue()

    @classmethod
    def build_breakdown_of_services_excel_report_for_cost_center(cls, cost_center, day, breakdown):
        logging.info(f"Building Excel report: breakdown of services for cost center '{cost_center}'")
        buffer = io.BytesIO()
        workbook = xlsxwriter.Workbook(buffer)
        amount_format = workbook.add_format({'num_format': '# ##0.00'})
        amount_format.set_align('right')
        worksheet = workbook.add_worksheet()
        headers = ['Month', 'Cost Center', 'Organizational Unit', 'Account', 'Name', 'Service', 'Amount (USD)']
        worksheet.write_row(0, 0, headers)
        widths = {index: len(headers[index]) for index in range(len(headers))}
        row = 1
        for item in breakdown:
            data = [day.isoformat()[:7],
                    str(cost_center),
                    str(item['unit']),
                    str(item['account']),
                    str(item['name']),
                    str(item['service']),
                    float(item['amount'])]
            worksheet.write_row(row, 0, data)
            for index in range(len(data)):
                widths[index] = max(widths[index], len(str(data[index])))
            row += 1
        worksheet.write(row, 0, day.isoformat()[:7])
        worksheet.write(row, 1, cost_center)
        worksheet.write(row, 2, 'TOTAL')
        worksheet.write(row, 6, "=SUM(G2:{})".format(xl_rowcol_to_cell(row - 1, 6)))
        for index in range(6):
            worksheet.set_column(index, index, widths[index])
        worksheet.set_column(6, 6, widths[6], amount_format)
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
        headers = ['Month', 'Cost Center', 'Organizational Unit', 'Account', 'Charges (USD)']
        headers.extend(sorted(list(labels.values())))
        logging.debug(headers)
        writer = DictWriter(buffer, fieldnames=headers)
        writer.writeheader()
        for cost_center in sorted(charges.keys()):
            units = {}
            for item in charges[cost_center]:
                accounts = units.get(item['unit']) or {}
                label = f"{item['name']} ({item['account']})"
                values = accounts.get(label) or []
                values.append(item)
                accounts[label] = values
                units[item['unit']] = accounts
            for name in sorted(units.keys()):
                accounts = units[name]
                for account in sorted(accounts.keys()):
                    total = 0.0
                    row = {'Month': day.isoformat()[:7],
                           'Cost Center': cost_center,
                           'Organizational Unit': name,
                           'Account': account}
                    for item in accounts[account]:
                        header = labels[item['charge']]
                        amount = float(item['amount'])
                        row[header] = amount
                        total += amount
                    row['Charges (USD)'] = total
                    logging.debug(row)
                    writer.writerow(row)
        return buffer.getvalue()

    @classmethod
    def build_summary_of_charges_excel_report(cls, charges, day, currency='USD', rate=1.0):
        logging.info(f"Building Excel report: summary of charges in {currency}")
        buffer = io.BytesIO()
        workbook = xlsxwriter.Workbook(buffer)
        worksheet = workbook.add_worksheet()
        types = set()
        for cost_center in charges.keys():
            types = types.union(set(item['charge'] for item in charges[cost_center]))
        labels = sorted(types)
        headers = ['Month', 'Cost Center', 'Organizational Unit', 'Account', f"Charges ({currency})"]
        headers.extend([f"{label} ({currency})" for label in labels])
        logging.debug(headers)
        worksheet.write_row(0, 0, headers)
        widths = {index: len(headers[index]) for index in range(len(headers))}
        units_subs = []
        row = 1
        month = day.isoformat()[:7]
        for cost_center in sorted(charges.keys()):
            units = cls.set_breakdowns_per_unit_and_per_account(items=charges[cost_center])
            accounts_subs = []
            for unit in sorted(units.keys()):
                unit_head = row
                accounts = units[unit]
                for account in sorted(accounts.keys()):
                    total = 0.0
                    data = [month, str(cost_center), unit, str(account)]
                    amounts = accounts[account]
                    for amount in amounts.values():
                        total += amount * rate
                    data.append(total)
                    for label in labels:
                        data.append(amounts.get(label, 0.0) * rate)
                    logging.debug(data)
                    worksheet.write_row(row, 0, data)
                    worksheet.set_row(row, None, None, {'level': 3, 'hidden': True})
                    for index in range(len(data)):
                        widths[index] = max(widths[index], len(str(data[index])))
                    row += 1
                cls.set_unit_row(worksheet=worksheet, row=row, month=month, cost=str(cost_center), unit=unit, unit_head=unit_head, columns=len(labels))
                accounts_subs.append([xl_rowcol_to_cell(row, 4 + delta) for delta in range(1 + len(labels))])
                row += 1
            cls.set_cost_row(worksheet=worksheet, row=row, month=month, cost=str(cost_center), subs=accounts_subs)
            units_subs.append([xl_rowcol_to_cell(row, 4 + delta) for delta in range(1 + len(labels))])
            row += 1
        cls.set_total_row(worksheet=worksheet, row=row, month=month, subs=units_subs)
        cls.set_columns(workbook=workbook, worksheet=worksheet, widths=widths)
        workbook.close()
        return buffer.getvalue()

    @classmethod
    def build_summary_of_services_csv_report(cls, costs, day):
        logging.info("Building CSV report: summary of services")
        buffer = io.StringIO()
        writer = DictWriter(buffer, fieldnames=['Month', 'Cost Center', 'Organizational Unit', 'Amount (USD)'])
        writer.writeheader()
        summary = 0.0
        for cost_center in sorted(costs.keys()):
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
                row = {'Month': day.isoformat()[:7],
                       'Cost Center': cost_center,
                       'Organizational Unit': name,
                       'Amount (USD)': units[name]}
                writer.writerow(row)
            row = {'Month': day.isoformat()[:7],
                   'Cost Center': cost_center,
                   'Organizational Unit': '',
                   'Amount (USD)': total}
            writer.writerow(row)
        row = {'Month': day.isoformat()[:7],
               'Cost Center': 'TOTAL',
               'Organizational Unit': '',
               'Amount (USD)': summary}
        writer.writerow(row)
        return buffer.getvalue()

    @classmethod
    def build_summary_of_services_excel_report(cls, costs, day):
        logging.info("Building Excel report: summary of services")
        buffer = io.BytesIO()
        workbook = xlsxwriter.Workbook(buffer)
        amount_format = workbook.add_format({'num_format': '# ##0.00'})
        amount_format.set_align('right')
        worksheet = workbook.add_worksheet()
        headers = ['Month', 'Cost Center', 'Organizational Unit', 'Amount (USD)']
        worksheet.write_row(0, 0, headers)
        widths = {index: len(headers[index]) for index in range(len(headers))}
        subs = []
        row = 1
        month = day.isoformat()[:7]
        for cost_center in sorted(costs.keys()):
            head = row
            units = {}
            for item in costs[cost_center]:
                amount = float(item['amount'])
                name = item['unit']
                value = units.get(name, 0.0)
                units[name] = value + amount
            for name in units.keys():
                data = [month, str(cost_center), name, units[name]]
                worksheet.write_row(row, 0, data)
                worksheet.set_row(row, None, None, {'level': 2, 'hidden': True})
                row += 1
            data = [month,
                    str(cost_center),
                    '',
                    f"=SUM({xl_rowcol_to_cell(head, 3)}:{xl_rowcol_to_cell(row - 1, 3)})"]
            worksheet.write_row(row, 0, data)
            worksheet.set_row(row, None, None, {'level': 1, 'collapsed': True})
            subs.append(xl_rowcol_to_cell(row, 3))
            row += 1
            for index in range(len(data)):
                widths[index] = max(widths[index], len(str(data[index])))
        worksheet.write(row, 0, month)
        worksheet.write(row, 1, 'TOTAL')
        worksheet.write(row, 3, '=' + '+'.join(subs))
        for index in range(3):
            worksheet.set_column(index, index, widths[index])
        worksheet.set_column(3, 3, widths[2], amount_format)
        workbook.close()
        return buffer.getvalue()

    @classmethod
    def set_breakdowns_per_unit_and_per_account(cls, items):
        units = {}
        for item in items:
            accounts = units.get(item['unit']) or {}
            label = f"{item['name']} ({item['account']})"
            amounts = accounts.get(label) or {}
            amounts[item['charge']] = float(item['amount'])
            accounts[label] = amounts
            units[item['unit']] = accounts
        return units

    @classmethod
    def set_columns(cls, workbook, worksheet, widths):
        amount_format = workbook.add_format({'num_format': '# ##0.00'})
        amount_format.set_align('right')
        for index in range(len(widths)):
            if index > 3:
                worksheet.set_column(index, index, widths[index], amount_format)
            else:
                worksheet.set_column(index, index, widths[index])

    @classmethod
    def set_cost_row(cls, worksheet, row, month, cost, subs):
        data = [month, cost, '', '']
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
        worksheet.set_row(row, None, None, {'level': 1, 'collapsed': True})

    @classmethod
    def set_total_row(cls, worksheet, row, month, subs):
        data = [month, 'TOTAL', '', '']
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
    def set_unit_row(cls, worksheet, row, month, cost, unit, unit_head, columns):
        data = [month, cost, unit, '']
        for delta in range(1 + columns):
            data.append(f"=SUM({xl_rowcol_to_cell(unit_head, 4 + delta)}:{xl_rowcol_to_cell(row - 1, 4 + delta)})")
        logging.debug(data)
        worksheet.write_row(row, 0, data)
        worksheet.set_row(row, None, None, {'level': 2, 'hidden': True})
