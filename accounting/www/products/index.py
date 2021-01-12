import frappe

def get_context(context):
	context.items = frappe.get_list('Item', fields=['name', 'item_description', 'image', 'route', 'standard_selling_rate'])
	return context