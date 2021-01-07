# -*- coding: utf-8 -*-
# Copyright (c) 2021, Shariq and Contributors
# See license.txt
from __future__ import unicode_literals

import frappe
import unittest
from frappe.utils import flt, nowdate
from accounting.accounting.doctype.company.test_company import create_company

class TestPurchaseOrder(unittest.TestCase):

	def setUp(self):
		create_company('_Test Company')

	def test_purchase_order_creation(self):
		po = make_purchase_order('Poco F2', 10, 'Dinesh Supplier', True, False)
		self.assertTrue(get_purchase_order(po.name))
		items_quantity, items_amount = 0, 0
		for item in po.items:
			items_quantity += flt(item.qty)
			items_amount += flt(item.amount)
		self.assertEqual(po.total_quantity, items_quantity)
		self.assertEqual(po.total_amount, items_amount)
	
	def test_purchase_order_validation(self):
		po = make_purchase_order('Poco F2', -10, 'Dinesh Supplier', False, False)
		self.assertRaises(frappe.exceptions.ValidationError, po.insert)

		po = make_purchase_order('Poco F2', 0, 'Dinesh Supplier', False, False)
		self.assertRaises(frappe.exceptions.ValidationError, po.insert)

def make_purchase_order(item_name, qty, party, save=True, submit=False):
	po = frappe.new_doc("Purchase Order")
	po.party = party
	po.posting_date = nowdate()
	po.schedule_date = nowdate()
	po.company = '_Test Company'
	po.set("items",[
		{
			"item": item_name,
			"qty": qty
		}
	])

	if save or submit:
		po.insert()
		if submit:
			po.submit()
	
	return po

def get_purchase_order(name):
	return frappe.db.sql(""" select * from `tabPurchase Order` where name=%s """, name, as_dict=1)