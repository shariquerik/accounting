# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt
from __future__ import unicode_literals

import frappe

def get_context(context):
	context.items = frappe.db.get_list('Item',
						fields=['name', 'item_description', 'image', 'route', 'standard_selling_rate'],
						ignore_permissions=True)
	return context