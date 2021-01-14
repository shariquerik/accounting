// Copyright (c) 2021, Shariq and contributors
// For license information, please see license.txt

frappe.ui.form.on('Delivery Note', {
	refresh: function(frm) {
		cur_frm.add_custom_button(__("Sales Invoice"), function() {
			get_doc(cur_frm.docname).then(
				function(result) { 
					frappe.model.with_doctype('Sales Invoice', function() {
						var si = frappe.model.get_new_doc('Sales Invoice');
						si.party = frm.doc.party;
						si.company = frm.doc.company;
						si.total_quantity = frm.doc.total_quantity;
						si.total_amount = frm.doc.total_amount;
						result.forEach(function(item) {
							var si_item = frappe.model.add_child(si, 'items');
							si_item.item = item.item;
							si_item.qty = item.qty;
							si_item.rate = item.rate;
							si_item.amount = item.amount;
						});
						frappe.set_route('Form', 'Sales Invoice', si.name);
					});
				}
			);
		}, __("Create"));

		frm.page.set_inner_btn_group_as_primary(__('Create'));

		var get_doc = function(mydocname){
			var si;
			return new Promise(function(resolve) {
				frappe.call({
					"method": "frappe.client.get",
					"args": {
						"doctype": "Delivery Note",
						"name": mydocname
					},
					"callback": function(response) {
						si = response.message.items;   
						resolve(si);
					}
				});
			});
		} 
	},
	setup: function(frm) {
		frappe.db.get_doc('Company', frm.doc.company)
		.then(doc => {
			frm.set_value('debit_to', doc.default_cost_of_goods_sold_account);
			frm.set_value('income_account', doc.default_inventory_account);
		})
	}
});

frappe.ui.form.on("Delivery Note Item", {
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
				frappe.model.set_value(cdt, cdn, 'rate', doc.standard_purchase_rate)
			})
		}
	}
});
var calculate_total = function(frm, cdt, cdn) {
	var child = locals[cdt][cdn];
	frappe.model.set_value(cdt, cdn, "amount", child.qty * child.rate);
}


frappe.ui.form.on("Delivery Note Item", "qty", function(frm, cdt, cdn) {
	var delivery_item_details = frm.doc.items;
	var total = 0
	for(var i in delivery_item_details) {
		total = total + delivery_item_details[i].qty
	}
	frm.set_value("total_quantity", total)
});

frappe.ui.form.on("Delivery Note Item", "amount", function(frm, cdt, cdn) {
	var delivery_item_details = frm.doc.items;
	var total = 0
	for(var i in delivery_item_details) {
		total = total + delivery_item_details[i].amount
	}
	frm.set_value("total_amount", total)
});
