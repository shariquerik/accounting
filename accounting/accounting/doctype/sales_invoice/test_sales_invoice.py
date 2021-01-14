# -*- coding: utf-8 -*-
# Copyright (c) 2020, Shariq and Contributors
# See license.txt
from __future__ import unicode_literals

import frappe
import unittest
from frappe.utils import flt, nowdate
from accounting.accounting.doctype.company.test_company import create_company
from accounting.accounting.doctype.journal_entry.test_journal_entry import get_gl_entries

class TestSalesInvoice(unittest.TestCase):

	def setUp(self):
		create_company('_Test Company')

	def test_sales_invoice_creation(self):
		si = make_sales_invoice('Poco F2', 10, 'Rohan', True, False)
		self.assertTrue(get_sales_invoice(si.name))
		items_quantity, items_amount = 0, 0
		for item in si.items:
			items_quantity += flt(item.qty)
			items_amount += flt(item.amount)
		self.assertEqual(si.total_quantity, items_quantity)
		self.assertEqual(si.total_amount, items_amount)
	
	def test_sales_invoice_validation(self):
		si = make_sales_invoice('Poco F2', -10, 'Rohan', False, False)
		self.assertRaises(frappe.exceptions.ValidationError, si.insert)

		si = make_sales_invoice('Poco F2', 0, 'Rohan', False, False)
		self.assertRaises(frappe.exceptions.ValidationError, si.insert)

	def test_gl_entry_creation(self):
		si = make_sales_invoice('Poco F2', 10, 'Rohan', True, True)
		gl_entries = get_gl_entries(si.name, 'Sales Invoice')
		self.assertTrue(gl_entries)

		for gle in gl_entries:
			if gle.account == si.income_account:
				self.assertEqual(gle.debit_amount, 0)
				self.assertEqual(gle.credit_amount, 120000)
			else:
				self.assertEqual(gle.credit_amount, 0)
				self.assertEqual(gle.debit_amount, 120000)

	def test_reverse_gl_entry(self):
		si = make_sales_invoice('Poco F2', 10, 'Rohan', True, True)
		gl_entries_before = get_gl_entries(si.name, 'Sales Invoice')
		si.cancel()
		gl_entries_after = get_gl_entries(si.name, 'Sales Invoice')

		# check if number of gl entries is double the gl entries before cancel
		self.assertEqual(len(gl_entries_after)/2, len(gl_entries_before))

		# check if the is_cancelled if True for all entries after cancel
		for gle in gl_entries_after:
			self.assertTrue(gle.is_cancelled)

def make_sales_invoice(item_name, qty, party, save=True, submit=False):
	si = frappe.new_doc("Sales Invoice")
	si.party = party
	si.posting_date = nowdate()
	si.company = '_Test Company'
	si.set("items",[
		{
			"item": item_name,
			"qty": qty
		}
	])

	if save or submit:
		si.insert()
		if submit:
			si.submit()
	
	return si

def get_sales_invoice(name):
	return frappe.db.sql(""" SELECT
						*
					FROM
						`tabSales Invoice`
					WHERE
						name=%s """, name, as_dict=1)

