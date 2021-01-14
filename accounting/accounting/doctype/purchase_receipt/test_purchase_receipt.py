# -*- coding: utf-8 -*-
# Copyright (c) 2021, Shariq and Contributors
# See license.txt
from __future__ import unicode_literals

import frappe
import unittest
from frappe.utils import flt, nowdate
from accounting.accounting.doctype.company.test_company import create_company
from accounting.accounting.doctype.journal_entry.test_journal_entry import get_gl_entries

class TestPurchaseReceipt(unittest.TestCase):

	def setUp(self):
		create_company('_Test Company')

	def test_purchase_receipt_creation(self):
		pr = make_purchase_receipt('Poco F2', 10, 'Dinesh Supplier', True, False)
		self.assertTrue(get_purchase_receipt(pr.name))
		items_quantity, items_amount = 0, 0
		for item in pr.items:
			items_quantity += flt(item.qty)
			items_amount += flt(item.amount)
		self.assertEqual(pr.total_quantity, items_quantity)
		self.assertEqual(pr.total_amount, items_amount)
	
	def test_purchase_receipt_validation(self):
		pr = make_purchase_receipt('Poco F2', -10, 'Dinesh Supplier', False, False)
		self.assertRaises(frappe.exceptions.ValidationError, pr.insert)

		pr = make_purchase_receipt('Poco F2', 0, 'Dinesh Supplier', False, False)
		self.assertRaises(frappe.exceptions.ValidationError, pr.insert)

	def test_gl_entry_creation(self):
		pr = make_purchase_receipt('Poco F2', 10, 'Dinesh Supplier', True, True)
		gl_entries = get_gl_entries(pr.name, 'Purchase Receipt')
		self.assertTrue(gl_entries)

		for gle in gl_entries:
			if gle.account == pr.expense_account:
				self.assertEqual(gle.debit_amount, 120000)
				self.assertEqual(gle.credit_amount, 0)
			else:
				self.assertEqual(gle.credit_amount, 120000)
				self.assertEqual(gle.debit_amount, 0)

	def test_reverse_gl_entry(self):
		pr = make_purchase_receipt('Poco F2', 10, 'Dinesh Supplier', True, True)
		gl_entries_before = get_gl_entries(pr.name, 'Purchase Receipt')
		pr.cancel()
		gl_entries_after = get_gl_entries(pr.name, 'Purchase Receipt')

		# check if number of gl entries is double the gl entries before cancel
		self.assertEqual(len(gl_entries_after)/2, len(gl_entries_before))

		# check if the is_cancelled if True for all entries after cancel
		for gle in gl_entries_after:
			self.assertTrue(gle.is_cancelled)

def make_purchase_receipt(item_name, qty, party, save=True, submit=False):
	pr = frappe.new_doc("Purchase Receipt")
	pr.party = party
	pr.posting_date = nowdate()
	pr.company = '_Test Company'
	pr.set("items",[
		{
			"item": item_name,
			"qty": qty
		}
	])

	if save or submit:
		pr.insert()
		if submit:
			pr.submit()
	
	return pr

def get_purchase_receipt(name):
	return frappe.db.sql(""" SELECT
						*
					FROM
						`tabPurchase Receipt`
					WHERE
						name=%s """, name, as_dict=1)
