// Copyright (c) 2016, Shariq and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Balance Sheet"] = {
	"filters": [
		{
			"fieldname":"company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_user_default("Company"),
			"reqd": 1
		},
		{
			"fieldname": "fiscal_year",
			"label": __("Fiscal Year"),
			"fieldtype": "Link",
			"options": "Fiscal Year",
			"reqd": 1,
			"default": frappe.defaults.get_user_default("Fiscal Year"),
			"width": "60px"
		},
		{
			"fieldname": "chart_type",
			"label": __("Chart_type"),
			"fieldtype": "Select",
			"options": ["Bar Chart", "Line Chart"],
			"default": "Bar Chart"
		}
	]
};
