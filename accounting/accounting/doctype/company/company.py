# -*- coding: utf-8 -*-
# Copyright (c) 2020, Shariq and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils.nestedset import NestedSet

class Company(NestedSet):

	def on_update(self):
		NestedSet.on_update(self)
		if not frappe.db.sql("""select name from tabAccount
				where company=%s and docstatus<2 limit 1""", self.name):
			self.create_accounts()

	def create_accounts(self):
		from accounting.accounting.doctype.account.chart_of_accounts.chart_of_accounts import create_charts
		frappe.local.flags.ignore_root_company_validation = True
		create_charts(self.name, self.abbr)
		self.set_default_accounts()
	
	def set_default_accounts(self):
		accounts = frappe.db.sql("""select
							name, account_type
						from
							tabAccount
						where
							company=%s
						""", self.company_name, as_dict=1)
		
		for account in accounts:
			if account.account_type:
				if account.account_type == 'Cash':
					self.default_cash_account = account.name
				elif account.account_type == 'Payable':
					self.default_payable_account = account.name
				elif account.account_type == 'Receivable':
					self.default_receivable_account = account.name
				elif account.account_type == 'Cost of Goods Sold':
					self.default_cost_of_goods_sold_account = account.name
				elif account.account_type == 'Income Account':
					self.default_income_account = account.name
				elif account.account_type == 'Stock':
					self.default_inventory_account = account.name
				elif account.account_type == 'Stock Received But Not Billed':
					self.stock_received_but_not_billed = account.name
				