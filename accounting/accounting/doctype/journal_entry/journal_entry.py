# -*- coding: utf-8 -*-
# Copyright (c) 2020, Shariq and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import flt
from accounting.accounting.general_ledger import make_gl_entry, make_reverse_gl_entry

class JournalEntry(Document):

	def validate(self):
		self.set_total_debit_credit()
		if self.difference:
			frappe.throw(_("Total Debit and Credit must be equal. The difference is {0}").format(
				self.difference))

	def set_total_debit_credit(self):
		self.total_debit, self.total_credit, self.difference = 0, 0, 0
		for d in self.accounting_entries:
			self.total_debit = flt(self.total_debit) + flt(d.debit)
			self.total_credit = flt(self.total_credit) + flt(d.credit)

		self.difference = flt(self.total_debit) - flt(self.total_credit)

	def on_submit(self):
		for d in self.accounting_entries:
			make_gl_entry(self, d.account, d.debit, d.credit)

	def on_cancel(self):
		self.ignore_linked_doctypes = ('GL Entry')
		make_reverse_gl_entry(voucher_type=self.doctype, voucher_no=self.name)
