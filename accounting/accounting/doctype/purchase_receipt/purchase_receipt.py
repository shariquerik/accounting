# -*- coding: utf-8 -*-
# Copyright (c) 2021, Shariq and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import flt
from frappe.model.document import Document
from accounting.accounting.general_ledger import make_gl_entry, make_reverse_gl_entry

class PurchaseReceipt(Document):

	def validate(self):
		self.validate_quantity()
		self.set_item_rate_amount()
		self.set_totals()
		self.set_accounts()
	
	def validate_quantity(self):
		for item in self.items:
			if item.qty <= 0:
				frappe.throw("One or more quantity is required for each product")

	def set_item_rate_amount(self):
		for item in self.items:
			item.rate = frappe.db.get_value('Item', item.item, 'standard_purchase_rate')
			item.amount = flt(item.qty) * item.rate

	def set_totals(self):
		self.total_quantity, self.total_amount = 0,0
		for item in self.items:
			self.total_quantity = flt(self.total_quantity) + flt(item.qty)
			self.total_amount = flt(self.total_amount) + flt(item.amount) 

	def set_accounts(self):
		if not self.expense_account:
			self.expense_account = frappe.db.get_value('Company', self.company, 'default_inventory_account')
		if not self.credit_to:
			self.credit_to = frappe.db.get_value('Company', self.company, 'stock_received_but_not_billed')

	def on_submit(self):
		make_gl_entry(self, self.expense_account, self.total_amount, 0)
		make_gl_entry(self, self.credit_to, 0, self.total_amount)

	def on_cancel(self):
		self.ignore_linked_doctypes = ('GL Entry')
		make_reverse_gl_entry(voucher_type=self.doctype, voucher_no=self.name)

@frappe.whitelist()
def make_purchase_invoice(source_name, target_doc=None):
	from frappe.model.mapper import get_mapped_doc

	doclist = get_mapped_doc("Purchase Receipt", source_name , {
		"Purchase Receipt": {
			"doctype": "Purchase Invoice",
			"field_map": {
				"total_amount": "total_amount"
			},
			"validation": {
				"docstatus": ["=", 1]
			}
		}
	}, target_doc)

	return doclist
