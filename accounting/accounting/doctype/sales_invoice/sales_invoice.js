// Copyright (c) 2020, Shariq and contributors
// For license information, please see license.txt

frappe.ui.form.on('Sales Invoice', {
	refresh: function(frm) {
		// frm.add_custom_button(__("Payment Entry"), function () {
		// 	frappe.model.open_mapped_doc({
		// 		method: "accounting.accounting.doctype.sales_invoice.sales_invoice.make_payment_entry",
		// 		frm: cur_frm
		// 	})
		// }, __("Create"));
		// frm.page.set_inner_btn_group_as_primary(__('Create'));

		cur_frm.add_custom_button(__("Payment Entry"), function() {
			frappe.model.with_doctype('Payment Entry', function() {
				var pe = frappe.model.get_new_doc('Payment Entry');
				pe.party = frm.doc.party;
				pe.company = frm.doc.company;
				pe.paid_amount = frm.doc.total_amount;
				pe.payment_type = 'Receive'
				frappe.set_route('Form', 'Payment Entry', pe.name);
			});
		}, __("Create"));

		frm.page.set_inner_btn_group_as_primary(__('Create'));
	},
	setup: function(frm) {
		frappe.db.get_doc('Company', frm.doc.company)
		.then(doc => {
			frm.set_value('debit_to', doc.default_receivable_account);
			frm.set_value('income_account', doc.default_income_account);
		})
	}
});

frappe.ui.form.on("Sales Invoice Item", {
	qty: function(frm,cdt,cdn){
		calculate_total(frm, cdt, cdn);
	},
	rate: function(frm, cdt, cdn){
		calculate_total(frm, cdt, cdn);
	},
	item: function(frm,cdt,cdn){
		var child = locals[cdt][cdn];
		if(child.item){
			frappe.db.get_doc('Item', child.item)
			.then( doc =>{
				frappe.model.set_value(cdt, cdn, 'qty', 1.00)
				frappe.model.set_value(cdt, cdn, 'rate', doc.standard_selling_rate)
			})
		}
	}
});
var calculate_total = function(frm, cdt, cdn) {
	var child = locals[cdt][cdn];
	frappe.model.set_value(cdt, cdn, "amount", child.qty * child.rate);
}


frappe.ui.form.on("Sales Invoice Item", "qty", function(frm, cdt, cdn) {
	var sales_item_details = frm.doc.items;
	var total = 0
	for(var i in sales_item_details) {
		total = total + sales_item_details[i].qty
	}
	frm.set_value("total_quantity", total)
});

frappe.ui.form.on("Sales Invoice Item", "amount", function(frm, cdt, cdn) {
	var sales_item_details = frm.doc.items;
	var total = 0
	for(var i in sales_item_details) {
		total = total + sales_item_details[i].amount
	}
	frm.set_value("total_amount", total)
});