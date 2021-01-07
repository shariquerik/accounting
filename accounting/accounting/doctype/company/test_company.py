# -*- coding: utf-8 -*-
# Copyright (c) 2020, Shariq and Contributors
# See license.txt
from __future__ import unicode_literals

import frappe
import unittest

class TestCompany(unittest.TestCase):

	def test_company_created(self):
		self.assertTrue(create_company('_Test Company Again'))

def create_company(company_name):
	abbr = "".join(c[0].upper() for c in company_name.split())
	company = frappe.db.get_value('Company', filters={'company_name': company_name})
	if company:
		return company
	else:
		company = frappe.new_doc("Company")
		company.company_name = company_name
		company.abbr = abbr
		company.insert()
		return company
