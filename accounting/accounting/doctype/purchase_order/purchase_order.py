# -*- coding: utf-8 -*-
# Copyright (c) 2021, Shariq and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class PurchaseOrder(Document):
	pass

@frappe.whitelist()
def make_purchase_receipt(source_name, target_doc=None):
	from frappe.model.mapper import get_mapped_doc

	doclist = get_mapped_doc("Purchase Order", source_name , {
		"Purchase Order": {
			"doctype": "Purchase Receipt",
			"field_map": {
				"party": "party"
			},
			"validation": {
				"docstatus": ["=", 1]
			}
		}
	}, target_doc)

	return doclist
