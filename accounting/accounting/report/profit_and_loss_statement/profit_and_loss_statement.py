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

	income_accounts = get_account_list(filters, 'Income', balance_label)
	expense_accounts = get_account_list(filters, 'Expense', balance_label)
	chart = get_chart_data(filters, columns, income_accounts, expense_accounts, data[-1][balance_label])

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

	income_accounts = get_account_list(filters, 'Income', balance_label)
	expense_accounts = get_account_list(filters, 'Expense', balance_label)

	if income_accounts:
		append_accounts_and_total(data, income_accounts, 'Total Income (Credit)',balance_label)
	if expense_accounts:
		append_accounts_and_total(data, expense_accounts, 'Total Expense (Debit)', balance_label)

	profit_loss, debit, credit = get_profit_loss_amount(data, balance_label)
	data.append({ "account": 'Profit for the year', balance_label: profit_loss })

	return data

def get_account_list(filters, root_type, balance_label):
	accounts = []
	gl_entries = frappe.db.sql(
		"""
		select distinct(account)
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

def get_profit_loss_amount(data, balance_label):
	debit, credit = 0,0
	for d in data:
		if d['account'] == 'Total Income (Credit)':
			credit = d[balance_label]
		elif d['account'] == 'Total Expense (Debit)':
			debit = d[balance_label]
	profit_loss = credit - debit
	return profit_loss, debit, credit

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
	profit, expense, income = get_profit_loss_amount(data, balance_label)

	report_summary = [
		{
			"value": income,
			"label": "Income",
			"datatype": "Currency",
			"currency": "₹"
		},
		{
			"value": expense,
			"label": "Expense",
			"datatype": "Currency",
			"currency": "₹"
		},
		{
			"value": profit,
			"indicator": "Green" if profit > 0 else "Red",
			"label": "Total Profit This Year",
			"datatype": "Currency",
			"currency": "₹"
		}
	]
	return report_summary

def get_chart_data(filters, columns, income, expense, profit):
	labels = [d.get("label") for d in columns[1:]]

	income_data, expense_data, profit_data = [], [], []

	for p in columns[1:]:
		if income:
			income_data.append(income[0].get(p.get("fieldname")))
		if expense:
			expense_data.append(expense[0].get(p.get("fieldname")))
		if profit:
			profit_data.append(profit)
	
	datasets = []
	if income_data:
		datasets.append({'name': 'Income', 'values': income_data})
	if expense_data:
		datasets.append({'name': 'Expense', 'values': expense_data})
	if profit_data:
		datasets.append({'name': 'Net Profit/Loss', 'values': profit_data})

	chart = {
		"data": {
			'labels': labels,
			'datasets': datasets
		}
	}

	chart["type"] = "bar"

	return chart
