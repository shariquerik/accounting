# -*- coding: utf-8 -*-
# Copyright (c) 2020, Shariq and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from accounting.accounting.general_ledger import make_gl_entry, make_reverse_gl_entry

class PaymentEntry(Document):

	def on_submit(self):
		make_gl_entry(self, self.paid_from, 0, self.paid_amount)
		make_gl_entry(self, self.paid_to, self.paid_amount, 0)

	def on_cancel(self):
		self.ignore_linked_doctypes = ('GL Entry')
		make_reverse_gl_entry(voucher_type=self.doctype, voucher_no=self.name)
