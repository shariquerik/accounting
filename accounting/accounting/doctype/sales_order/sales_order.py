# -*- coding: utf-8 -*-
# Copyright (c) 2021, Shariq and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class SalesOrder(Document):
	pass

@frappe.whitelist()
def make_delivery_note(source_name, target_doc=None):
	from frappe.model.mapper import get_mapped_doc

	doclist = get_mapped_doc("Sales Order", source_name , {
		"Sales Order": {
			"doctype": "Delivery Note",
			"field_map": {
				"party": "party"
			},
			"validation": {
				"docstatus": ["=", 1]
			}
		}
	}, target_doc)

	return doclist