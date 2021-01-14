# -*- coding: utf-8 -*-
# Copyright (c) 2021, Shariq and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import flt, nowdate
from frappe.model.document import Document

class SalesOrder(Document):

	def validate(self):
		self.validate_quantity()
		self.set_item_rate_amount_date()
		self.set_totals()
	
	def validate_quantity(self):
		for item in self.items:
			if item.qty <= 0:
				frappe.throw("One or more quantity is required for each product")

	def set_item_rate_amount_date(self):
		for item in self.items:
			item.delivery_date = nowdate()
			item.rate = frappe.db.get_value('Item', item.item, 'standard_purchase_rate')
			item.amount = flt(item.qty) * item.rate

	def set_totals(self):
		self.total_quantity, self.total_amount = 0,0
		for item in self.items:
			self.total_quantity = flt(self.total_quantity) + flt(item.qty)
			self.total_amount = flt(self.total_amount) + flt(item.amount) 