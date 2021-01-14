// Copyright (c) 2021, Shariq and contributors
// For license information, please see license.txt

frappe.ui.form.on('Sales Order', {
	refresh: function(frm) {
		cur_frm.add_custom_button(__("Delivery Note"), function() {
			get_doc(cur_frm.docname).then(
				function(result) { 
					frappe.model.with_doctype('Delivery Note', function() {
						var dn = frappe.model.get_new_doc('Delivery Note');
						dn.party = frm.doc.party;
						dn.company = frm.doc.company;
						dn.total_quantity = frm.doc.total_quantity;
						dn.total_amount = frm.doc.total_amount;
						result.forEach(function(item) {
							var dn_item = frappe.model.add_child(dn, 'items');
							dn_item.item = item.item;
							dn_item.qty = item.qty;
							dn_item.rate = item.rate;
							dn_item.amount = item.amount;
						});
						frappe.set_route('Form', 'Delivery Note', dn.name);
					});
				}
			);
		}, __("Create"));

		frm.page.set_inner_btn_group_as_primary(__('Create'));

		var get_doc = function(mydocname){
			var dn;
			return new Promise(function(resolve) {
				frappe.call({
					"method": "frappe.client.get",
					"args": {
						"doctype": "Sales Order",
						"name": mydocname
					},
					"callback": function(response) {
						dn = response.message.items;   
						resolve(dn);
					}
				});
			});
		} 
	}
});

frappe.ui.form.on("Sales Order Item", {
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
				frappe.model.set_value(cdt, cdn, 'delivery_date', frm.doc.delivery_date)
				frappe.model.set_value(cdt, cdn, 'rate', doc.standard_purchase_rate)
			})
		}
	}
});
var calculate_total = function(frm, cdt, cdn) {
	var child = locals[cdt][cdn];
	frappe.model.set_value(cdt, cdn, "amount", child.qty * child.rate);
}


frappe.ui.form.on("Sales Order Item", "qty", function(frm, cdt, cdn) {
	var sales_item_details = frm.doc.items;
	var total = 0
	for(var i in sales_item_details) {
		total = total + sales_item_details[i].qty
	}
	frm.set_value("total_quantity", total)
});

frappe.ui.form.on("Sales Order Item", "amount", function(frm, cdt, cdn) {
	var sales_item_details = frm.doc.items;
	var total = 0
	for(var i in sales_item_details) {
		total = total + sales_item_details[i].amount
	}
	frm.set_value("total_amount", total)
});
