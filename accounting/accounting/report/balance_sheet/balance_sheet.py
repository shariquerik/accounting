# Copyright (c) 2013, Shariq and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
	columns, data = [], []

	balance_label = "{}".format(filters.fiscal_year.replace(" ", "_").replace("-", "_"))

	columns = get_columns(filters)

	asset = get_data(filters.company, filters.fiscal_year, 'Asset', 'Debit',balance_label)
	liability = get_data(filters.company, filters.fiscal_year,'Liability', 'Credit',balance_label)
	equity = get_data(filters.company, filters.fiscal_year,'Equity', 'Credit',balance_label)

	data = []
	data.extend(asset or [])
	data.extend(liability or [])
	data.extend(equity or [])

	profit_loss, total, asset, liability, equity = get_profit_loss_total_amount(data, balance_label)
	data.append({ "account": 'Provisional Profit/Loss (Credit)', balance_label: profit_loss })
	data.append({ "account": 'Total (Credit)', balance_label: total })

	chart = get_chart_data(filters, columns, asset, liability, equity, balance_label)
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

def get_data(company, fiscal_year, root_type, dr_cr, balance_label):
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
		bal = get_account_balance(d['account'], fiscal_year)
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

def get_account_balance(account, fiscal_year):
	year = frappe.db.sql("""select year, year_start_date, year_end_date from `tabFiscal Year` where year=%s""",fiscal_year, as_dict=1)[0]
	return frappe.db.sql("""SELECT 
					sum(debit_amount) - sum(credit_amount) 
				FROM 
					`tabGL Entry` 
				WHERE 
					is_cancelled=0 and account=%s and posting_date>=%s and posting_date<=%s""",
				(account, year.year_start_date, year.year_end_date))[0][0]

def get_profit_loss_total_amount(data, balance_label):
	debit, credit, l_credit, e_credit = 0,0,0,0
	for d in data:
		if d and d['account'] == 'Total Asset (Debit)':
			debit = d[balance_label]
		elif d and d['account'] == 'Total Liability (Credit)':
			l_credit = d[balance_label]
			credit = d[balance_label]
		elif d and d['account'] == 'Total Equity (Credit)':
			e_credit = d[balance_label]
			credit += d[balance_label]
	profit_loss = debit - credit
	total = profit_loss + credit
	return profit_loss, total, debit, l_credit, e_credit

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

def get_chart_data(filters, columns, asset, liability, equity, balance_label):
	labels = [balance_label]

	asset_data, liability_data, equity_data = [], [], []

	if asset != 0:
		asset_data.append(asset)
	if liability != 0:
		liability_data.append(liability)
	if equity != 0:
		equity_data.append(equity)

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
