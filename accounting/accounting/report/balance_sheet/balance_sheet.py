# Copyright (c) 2013, Shariq and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from accounting.accounting.general_ledger import get_account_balance

def execute(filters=None):
	columns, data = [], []

	balance_label = "{}".format(filters.fiscal_year.replace(" ", "_").replace("-", "_"))

	columns = get_columns(filters)
	data = get_data(filters, balance_label)
	report_summary = get_report_summary(data, balance_label)

	asset_accounts = get_account_list(filters, 'Asset', balance_label)
	liability_accounts = get_account_list(filters, 'Liability', balance_label)
	equity_accounts = get_account_list(filters, 'Equity', balance_label)

	chart = get_chart_data(filters, columns, asset_accounts, liability_accounts, equity_accounts)

	return columns, data, None, chart, report_summary

def get_columns(filters):
	columns = [
		{
			"fieldname": "account",
			"label": "Account",
			"fieldtype": "Link",
			"options": "Account",
			"width": 300
		},
		{
			"fieldname": filters.fiscal_year.replace(" ", "_").replace("-", "_"),
			"label": filters.fiscal_year,
			"fieldtype": "Currency",
			"options": "currency",
			"width": 150
		}
	]
	return columns

def get_data(filters, balance_label):
	data = []

	asset_accounts = get_account_list(filters, 'Asset', balance_label)
	liability_accounts = get_account_list(filters, 'Liability', balance_label)
	equity_accounts = get_account_list(filters, 'Equity', balance_label)

	if asset_accounts:
		append_accounts_and_total(data, asset_accounts, 'Total Asset (Debit)',balance_label)
	if liability_accounts:
		append_accounts_and_total(data, liability_accounts, 'Total Liability (Credit)', balance_label)
	if equity_accounts:
		append_accounts_and_total(data, equity_accounts, 'Total Equity (Credit)', balance_label)

	profit_loss, total, a, b, c = get_profit_loss_total_amount(data, balance_label)
	data.append({ "account": 'Provisional Profit/Loss (Credit)', balance_label: profit_loss })
	data.append({ "account": 'Total (Credit)', balance_label: total })

	return data

def get_account_list(filters, root_type, balance_label):
	accounts = []
	gl_entries = frappe.db.sql(
		"""
		select distinct(account), posting_date
		from `tabGL Entry` 
		where {conditions} and account in (select name from tabAccount where root_type=%s)
		order by account
		""".format(conditions=get_conditions(filters)), root_type, as_dict=1)

	for gl_entry in gl_entries:
		balance = abs(get_account_balance(gl_entry.account))
		if balance:
			accounts.append({
				"account": gl_entry.account,
				"root_type": root_type,
				balance_label: balance
			})
	return accounts

def append_accounts_and_total(data, accounts, label, balance_label):
	data += accounts
	balance = 0
	for account in accounts:
		balance += account[balance_label]
	data.append({ "account": label, balance_label: balance })
	data.append({ "account": '' })

def get_profit_loss_total_amount(data, balance_label):
	debit, credit, l_credit, e_credit = 0,0,0,0
	for d in data:
		if d['account'] == 'Total Asset (Debit)':
			debit = d[balance_label]
		elif d['account'] == 'Total Liability (Credit)':
			l_credit = d[balance_label]
			credit = d[balance_label]
		elif d['account'] == 'Total Equity (Credit)':
			e_credit = d[balance_label]
			credit += d[balance_label]
	profit_loss = debit - credit
	total = profit_loss + credit
	return profit_loss, total, debit, l_credit, e_credit

def get_conditions(filters):
	conditions = []

	if filters.get("company"):
		conditions.append("company='{}'".format(filters.company))

	year = frappe.db.sql("""select * from `tabFiscal Year` where year=%s""",filters.fiscal_year,as_dict=1)[0]

	conditions.append("posting_date>='{}'".format(year.year_start_date))
	conditions.append("posting_date<='{}'".format(year.year_end_date))
	conditions.append("is_cancelled=0")

	return "{}".format(" and ".join(conditions)) if conditions else ""

def get_report_summary(data, balance_label):
	profit, total, asset, liability, equity = get_profit_loss_total_amount(data, balance_label)

	report_summary = [
		{
			"value": asset,
			"indicator": "Green",
			"label": "Total Asset",
			"datatype": "Currency",
			"currency": "₹"
		},
		{
			"value": liability,
			"indicator": "Red",
			"label": "Total Liability",
			"datatype": "Currency",
			"currency": "₹"
		},
		{
			"value": equity,
			"indicator": "Blue",
			"label": "Total Equity",
			"datatype": "Currency",
			"currency": "₹"
		},
		{
			"value": profit,
			"indicator": "Green" if profit > 0 else "Red",
			"label": "Provisional Profit / Loss (Credit)",
			"datatype": "Currency",
			"currency": "₹"
		}
	]
	return report_summary

def get_chart_data(filters, columns, asset, liability, equity):
	labels = [d.get("label") for d in columns[1:]]

	asset_data, liability_data, equity_data = [], [], []

	for p in columns[1:]:
		if asset:
			asset_data.append(asset[0].get(p.get("fieldname")))
		if liability:
			liability_data.append(liability[0].get(p.get("fieldname")))
		if equity:
			equity_data.append(equity[0].get(p.get("fieldname")))
	

	datasets = []
	if asset_data:
		datasets.append({'name': 'Assets', 'values': asset_data})
	if liability_data:
		datasets.append({'name': 'Liabilities', 'values': liability_data})
	if equity_data:
		datasets.append({'name': 'Equity', 'values': equity_data})

	chart = {
		"data": {
			'labels': labels,
			'datasets': datasets
		}
	}

	if filters.chart_type == "Bar Chart":
		chart["type"] = "bar"
	else:
		chart["type"] = "line"

	return chart
