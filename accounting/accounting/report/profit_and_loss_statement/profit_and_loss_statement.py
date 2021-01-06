# Copyright (c) 2013, Shariq and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from accounting.accounting.general_ledger import get_account_balance

def execute(filters=None):
	columns, data = [], []

	balance_label = "{}".format(filters.fiscal_year.replace(" ", "_").replace("-", "_"))

	columns = get_columns(filters)

	income = get_data(filters.company, 'Income', 'Credit',balance_label)
	expense = get_data(filters.company, 'Expense', 'Debit',balance_label)

	data = []
	data.extend(income or [])
	data.extend(expense or [])

	profit_loss, income, expense = get_profit_loss_amount(data, balance_label)
	data.append({ "account": 'Profit for the year', balance_label: profit_loss })

	chart = get_chart_data(filters, columns, income, expense, data[-1][balance_label], balance_label)
	report_summary = get_report_summary(data, balance_label)

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

def get_data(company, root_type, dr_cr,balance_label):
	accounts = get_accounts(company, root_type)
	data = []
	if accounts:
		i = 0
		for d in accounts:
			if d.parent_account == None or d.parent_account == data[-1]['account']:
				append(data, d, i, balance_label)
				i+=1
			else:
				for a in data:
					if a['account'] == d.parent_account:
						i = a['indent'] + 1
						break
				append(data, d, i, balance_label)
				i+=1
	temp=[]
	for d in data:
		bal = get_account_balance(d['account'])
		if bal:
			d[balance_label] = abs(bal)
			temp.append(d)
	for t in temp:
		for d in data:
			if d["account"] == t["parent_account"]:
				if d[balance_label] == 0:
					d[balance_label] = t[balance_label]
					temp.append(d)
				else:
					d[balance_label] += t[balance_label]
	data = [d for d in data if d[balance_label] != 0]
	if data:
		data.append({
			"account": "Total " + root_type + " (" + dr_cr + ")",
			balance_label: data[0][balance_label]
		})
		data.append({})
	return data

def append(data, d, i, balance_label):
	data.append({
		"account": d.name,
		"account_type": d.account_type,
		"parent_account": d.parent_account,
		"indent": i,
		"has_value": d.is_group,
		balance_label: 0
	})

def get_accounts(company, root_type):
	return frappe.db.sql(""" select name, parent_account, lft, root_type, account_type, is_group
			from 
				tabAccount
			where 
				company=%s and root_type=%s 
			order by 
				lft""", (company, root_type), as_dict=1)

def get_profit_loss_amount(data, balance_label):
	income, expense = 0,0
	for d in data:
		if d and d['account'] == 'Total Income (Credit)':
			income = d[balance_label]
		elif d and d['account'] == 'Total Expense (Debit)':
			expense = d[balance_label]
	profit_loss = income - expense
	return profit_loss, income, expense

def get_report_summary(data, balance_label):
	profit, income, expense = get_profit_loss_amount(data, balance_label)

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

def get_chart_data(filters, columns, income, expense, profit, balance_label):
	labels = [balance_label]

	income_data, expense_data, profit_data = [], [], []

	if income != 0:
		income_data.append(income)
	if expense != 0:
		expense_data.append(expense)
	if profit != 0:
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
