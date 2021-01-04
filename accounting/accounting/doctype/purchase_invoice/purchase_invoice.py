# -*- coding: utf-8 -*-
# Copyright (c) 2020, Shariq and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from accounting.accounting.general_ledger import make_gl_entry, make_reverse_gl_entry

class PurchaseInvoice(Document):

	def on_submit(self):
		make_gl_entry(self, self.expense_account, self.total_amount, 0)
		make_gl_entry(self, self.credit_to, 0, self.total_amount)

	def on_cancel(self):
		self.ignore_linked_doctypes = ('GL Entry')
		make_reverse_gl_entry(voucher_type=self.doctype, voucher_no=self.name)

@frappe.whitelist()
def make_payment_entry(source_name, target_doc=None):
	from frappe.model.mapper import get_mapped_doc

	doclist = get_mapped_doc("Purchase Invoice", source_name , {
		"Purchase Invoice": {
			"doctype": "Payment Entry",
			"field_map": {
				"total_amount": "paid_amount",
				"credit_to": "paid_to"
			},
			"validation": {
				"docstatus": ["=", 1]
			}
		}
	}, target_doc)

	return doclist