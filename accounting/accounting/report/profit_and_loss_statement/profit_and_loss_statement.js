// Copyright (c) 2016, Shariq and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Profit and Loss Statement"] = {
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
		}
	],
	"formatter": function(value, row, column, data, default_formatter) {
		if (data && column.fieldname=="account") {
			value = data.account || value;
			column.is_tree = true;
		}

		value = default_formatter(value, row, column, data);

		if (data && !data.parent_account) {
			value = $(`<span>${value}</span>`);

			var $value = $(value).css("font-weight", "bold");
			if (data.warn_if_negative && data[column.fieldname] < 0) {
				$value.addClass("text-danger");
			}

			value = $value.wrap("<p></p>").parent().html();
		}

		return value;
	},
	"tree": true,
	"name_field": "account",
	"parent_field": "parent_account",
	"initial_depth": 3
};
