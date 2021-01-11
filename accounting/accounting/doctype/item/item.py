# -*- coding: utf-8 -*-
# Copyright (c) 2020, Shariq and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
# import frappe
from frappe.website.website_generator import WebsiteGenerator

class Item(WebsiteGenerator):

	def validate(self):
		if not self.item_name:
			self.item_name = self.item_code