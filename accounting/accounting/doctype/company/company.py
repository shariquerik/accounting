# -*- coding: utf-8 -*-
# Copyright (c) 2020, Shariq and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils.nestedset import NestedSet

class Company(NestedSet):
	
	def on_update(self):
		NestedSet.on_update(self)
		self.create_accounts()

	def create_accounts(self):
		from accounting.accounting.doctype.account.chart_of_accounts.chart_of_accounts import create_charts
		frappe.local.flags.ignore_root_company_validation = True
		create_charts(self.name, self.abbr)