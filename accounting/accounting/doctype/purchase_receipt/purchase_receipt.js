// Copyright (c) 2021, Shariq and contributors
// For license information, please see license.txt

frappe.ui.form.on('Purchase Receipt', {
	refresh: function(frm) {
		// frm.add_custom_button(__("Purchase Invoice"), function () {
		// 	frappe.model.open_mapped_doc({
		// 		method: "accounting.accounting.doctype.purchase_receipt.purchase_receipt.make_purchase_invoice",
		// 		frm: cur_frm
		// 	})
		// }, __("Create"));
		// frm.page.set_inner_btn_group_as_primary(__('Create'));

		cur_frm.add_custom_button(__("Purchase Invoice"), function() {
			get_doc(cur_frm.docname).then(
				function(result) { 
					frappe.model.with_doctype('Purchase Invoice', function() {
						var pi = frappe.model.get_new_doc('Purchase Invoice');
						pi.party = frm.doc.party;
						pi.company = frm.doc.company;
						pi.total_quantity = frm.doc.total_quantity;
						pi.total_amount = frm.doc.total_amount;
						result.forEach(function(item) {
							var pi_item = frappe.model.add_child(pi, 'items');
							pi_item.item = item.item;
							pi_item.qty = item.qty;
							pi_item.rate = item.rate;
							pi_item.amount = item.amount;
						});
						frappe.set_route('Form', 'Purchase Invoice', pi.name);
					});
				}
			);
		}, __("Create"));

		frm.page.set_inner_btn_group_as_primary(__('Create'));

		var get_doc = function(mydocname){
			var pi;
			return new Promise(function(resolve) {
				frappe.call({
					"method": "frappe.client.get",
					"args": {
						"doctype": "Purchase Receipt",
						"name": mydocname
					},
					"callback": function(response) {
						pi = response.message.items;   
						resolve(pi);
					}
				});
			});
		} 
	},
	setup: function(frm) {
		frappe.db.get_doc('Company', frm.doc.company)
		.then(doc => {
			frm.set_value('expense_account', doc.default_inventory_account);
			frm.set_value('credit_to', doc.stock_received_but_not_billed);
		})
	}
});

frappe.ui.form.on("Purchase Receipt Item", {
	qty: function(frm,cdt,cdn){
		calculate_total(frm, cdt, cdn);
	},
	rate: function(frm, cdt, cdn){
		calculate_total(frm, cdt, cdn);
	},
	item: function(frm,cdt,cdn){
		debugger;
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
