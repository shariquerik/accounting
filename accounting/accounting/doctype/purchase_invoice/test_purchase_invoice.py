# -*- coding: utf-8 -*-
# Copyright (c) 2020, Shariq and Contributors
# See license.txt
from __future__ import unicode_literals

import frappe
import unittest
from frappe.utils import flt, nowdate
from accounting.accounting.doctype.company.test_company import create_company
from accounting.accounting.doctype.journal_entry.test_journal_entry import get_gl_entries

class TestPurchaseInvoice(unittest.TestCase):

	def setUp(self):
		create_company('_Test Company')

	def test_purchase_invoice_creation(self):
		pi = make_purchase_invoice('Poco F2', 10, 'Dinesh Supplier', True, False)
		self.assertTrue(get_purchase_invoice(pi.name))
		items_quantity, items_amount = 0, 0
		for item in pi.items:
			items_quantity += flt(item.qty)
			items_amount += flt(item.amount)
		self.assertEqual(pi.total_quantity, items_quantity)
		self.assertEqual(pi.total_amount, items_amount)
	
	def test_purchase_invoice_validation(self):
		pi = make_purchase_invoice('Poco F2', -10, 'Dinesh Supplier', False, False)
		self.assertRaises(frappe.exceptions.ValidationError, pi.insert)

		pi = make_purchase_invoice('Poco F2', 0, 'Dinesh Supplier', False, False)
		self.assertRaises(frappe.exceptions.ValidationError, pi.insert)

	def test_gl_entry_creation(self):
		pi = make_purchase_invoice('Poco F2', 10, 'Dinesh Supplier', True, True)
		gl_entries = get_gl_entries(pi.name, 'Purchase Invoice')
		self.assertTrue(gl_entries)

		for gle in gl_entries:
			if gle.account == pi.expense_account:
				self.assertEqual(gle.debit_amount, 120000)
				self.assertEqual(gle.credit_amount, 0)
			else:
				self.assertEqual(gle.credit_amount, 120000)
				self.assertEqual(gle.debit_amount, 0)

	def test_reverse_gl_entry(self):
		pi = make_purchase_invoice('Poco F2', 10, 'Dinesh Supplier', True, True)
		gl_entries_before = get_gl_entries(pi.name, 'Purchase Invoice')
		pi.cancel()
		gl_entries_after = get_gl_entries(pi.name, 'Purchase Invoice')

		# check if number of gl entries is double the gl entries before cancel
		self.assertEqual(len(gl_entries_after)/2, len(gl_entries_before))

		# check if the is_cancelled if True for all entries after cancel
		for gle in gl_entries_after:
			self.assertTrue(gle.is_cancelled)

def make_purchase_invoice(item_name, qty, party, save=True, submit=False):
	pi = frappe.new_doc("Purchase Invoice")
	pi.party = party
	pi.posting_date = nowdate()
	pi.company = '_Test Company'
	pi.set("items",[
		{
			"item": item_name,
			"qty": qty
		}
	])

	if save or submit:
		pi.insert()
		if submit:
			pi.submit()
	
	return pi

def get_purchase_invoice(name):
	return frappe.db.sql(""" select * from `tabPurchase Invoice` where name=%s """, name, as_dict=1)
