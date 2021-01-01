// Copyright (c) 2021, Shariq and contributors
// For license information, please see license.txt

frappe.ui.form.on('Purchase Receipt', {
	refresh: function(frm) {
		frm.add_custom_button(__("Purchase Invoice"), function () {
			frappe.model.open_mapped_doc({
				method: "accounting.accounting.doctype.purchase_receipt.purchase_receipt.make_purchase_invoice",
				frm: cur_frm
			})
		}, __("Create"));
		frm.page.set_inner_btn_group_as_primary(__('Create'));
	}
});

frappe.ui.form.on("Purchase Receipt Item", {
	qty: function(frm,cdt,cdn){
		calculate_total(frm, cdt, cdn);
	},
	rate: function(frm, cdt, cdn){
		calculate_total(frm, cdt, cdn);
	}
});
var calculate_total = function(frm, cdt, cdn) {
	var child = locals[cdt][cdn];
	frappe.model.set_value(cdt, cdn, "amount", child.qty * child.rate);
}


frappe.ui.form.on("Purchase Receipt Item", "qty", function(frm, cdt, cdn) {
	var purchase_item_details = frm.doc.items;
	var total = 0
	for(var i in purchase_item_details) {
		total = total + purchase_item_details[i].qty
	}
	frm.set_value("total_quantity", total)
});

frappe.ui.form.on("Purchase Receipt Item", "amount", function(frm, cdt, cdn) {
	var purchase_item_details = frm.doc.items;
	var total = 0
	for(var i in purchase_item_details) {
		total = total + purchase_item_details[i].amount
	}
	frm.set_value("total_amount", total)
});
