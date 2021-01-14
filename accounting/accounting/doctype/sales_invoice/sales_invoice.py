# -*- coding: utf-8 -*-
# Copyright (c) 2020, Shariq and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import flt, nowdate
from frappe.model.document import Document
from accounting.accounting.general_ledger import make_gl_entry, make_reverse_gl_entry

class SalesInvoice(Document):

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
			item.rate = frappe.db.get_value('Item', item.item, 'standard_selling_rate')
			item.amount = flt(item.qty) * item.rate

	def set_totals(self):
		self.total_quantity, self.total_amount = 0,0
		for item in self.items:
			self.total_quantity = flt(self.total_quantity) + flt(item.qty)
			self.total_amount = flt(self.total_amount) + flt(item.amount) 

	def set_accounts(self):
		if not self.income_account:
			self.income_account = frappe.db.get_value('Company', self.company, 'default_income_account')
		if not self.debit_to:
			self.debit_to = frappe.db.get_value('Company', self.company, 'default_receivable_account')

	def on_submit(self):
		make_gl_entry(self, self.income_account, 0, self.total_amount)
		make_gl_entry(self, self.debit_to, self.total_amount, 0)

	def on_cancel(self):
		self.ignore_linked_doctypes = ('GL Entry')
		make_reverse_gl_entry(voucher_type=self.doctype, voucher_no=self.name)

@frappe.whitelist(allow_guest=True)
def add_to_cart(item_name, qty, user, save=True, submit=False):
	user = user_exist(user)
	si_name = get_si(user)
	if si_name:
		return update_sales_invoice(item_name, qty, si_name, save, submit)
	else:
		return make_sales_invoice(item_name, qty, user, save, submit)

def user_exist(user):
	user_email = frappe.db.get_value('User', user, 'email')
	party = frappe.db.exists({ 'doctype': 'Party', 'party_email': user_email })
	if not party:
		party = frappe.new_doc('Party')
		party.party_name = user
		party.party_email = user_email
		party.party_type = 'Customer'
		party.insert()
		return party.name
	else:
		return party[0][0]

def get_si(user):
	doc = frappe.db.sql(""" SELECT
					name
				FROM
					`tabSales Invoice`
				WHERE
					party=%s and docstatus=0 order by modified desc""", user, as_dict=1)
	if not doc:
		return None
	else:
		return doc[0].name

@frappe.whitelist(allow_guest=True)
def make_sales_invoice(item_name, qty, party, save=True, submit=False):
	si = frappe.new_doc("Sales Invoice")
	si.party = party
	si.posting_date = nowdate()
	si.company = '_Test Company'
	si.set("items",[
		{
			"item": item_name,
			"qty": flt(qty)
		}
	])

	if save or submit:
		si.insert()
		if submit:
			si.submit()
	return si

@frappe.whitelist(allow_guest=True)
def update_sales_invoice(item_name, qty, si_name, save=True, submit=False):
	si = frappe.get_doc("Sales Invoice", si_name)
	items = si.items
	item_added = False
	if item_name:
		for item in items:
			if item.item == item_name:
				item.update({
					'qty': flt(item.qty) + flt(qty)
				})
				item_added = True
				break
		if not item_added:
			si.append('items', {
				'item': item_name,
				'qty': flt(qty)
			})
	if save or submit:
		si.save()
		if submit:
			si.submit()
	return si
