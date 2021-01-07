# -*- coding: utf-8 -*-
# Copyright (c) 2021, Shariq and Contributors
# See license.txt
from __future__ import unicode_literals

import frappe
import unittest
from frappe.utils import flt, nowdate
from accounting.accounting.doctype.company.test_company import create_company
from accounting.accounting.doctype.journal_entry.test_journal_entry import get_gl_entries

class TestDeliveryNote(unittest.TestCase):

	def setUp(self):
		create_company('_Test Company')

	def test_delivery_note_creation(self):
		dn = make_delivery_note('Poco F2', 10, 'Rohan', True, False)
		self.assertTrue(get_delivery_note(dn.name))
		items_quantity, items_amount = 0, 0
		for item in dn.items:
			items_quantity += flt(item.qty)
			items_amount += flt(item.amount)
		self.assertEqual(dn.total_quantity, items_quantity)
		self.assertEqual(dn.total_amount, items_amount)
	
	def test_delivery_note_validation(self):
		dn = make_delivery_note('Poco F2', -10, 'Rohan', False, False)
		self.assertRaises(frappe.exceptions.ValidationError, dn.insert)

		dn = make_delivery_note('Poco F2', 0, 'Rohan', False, False)
		self.assertRaises(frappe.exceptions.ValidationError, dn.insert)

	def test_gl_entry_creation(self):
		dn = make_delivery_note('Poco F2', 10, 'Rohan', True, True)
		gl_entries = get_gl_entries(dn.name, 'Delivery Note')
		self.assertTrue(gl_entries)

		for gle in gl_entries:
			if gle.account == dn.income_account:
				self.assertEqual(gle.debit_amount, 0)
				self.assertEqual(gle.credit_amount, 120000)
			else:
				self.assertEqual(gle.credit_amount, 0)
				self.assertEqual(gle.debit_amount, 120000)

	def test_reverse_gl_entry(self):
		dn = make_delivery_note('Poco F2', 10, 'Rohan', True, True)
		gl_entries_before = get_gl_entries(dn.name, 'Delivery Note')
		dn.cancel()
		gl_entries_after = get_gl_entries(dn.name, 'Delivery Note')

		# check if number of gl entries is double the gl entries before cancel
		self.assertEqual(len(gl_entries_after)/2, len(gl_entries_before))

		# check if the is_cancelled if True for all entries after cancel
		for gle in gl_entries_after:
			self.assertTrue(gle.is_cancelled)

def make_delivery_note(item_name, qty, party, save=True, submit=False):
	dn = frappe.new_doc("Delivery Note")
	dn.party = party
	dn.posting_date = nowdate()
	dn.company = '_Test Company'
	dn.set("items",[
		{
			"item": item_name,
			"qty": qty
		}
	])

	if save or submit:
		dn.insert()
		if submit:
			dn.submit()
	
	return dn

def get_delivery_note(name):
	return frappe.db.sql(""" select * from `tabDelivery Note` where name=%s """, name, as_dict=1)

