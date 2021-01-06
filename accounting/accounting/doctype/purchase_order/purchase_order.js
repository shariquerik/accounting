// Copyright (c) 2021, Shariq and contributors
// For license information, please see license.txt

frappe.ui.form.on('Purchase Order', {
	refresh: function(frm) {
		// frm.add_custom_button(__("Purchase Receipt"), function () {
		// 	frappe.model.open_mapped_doc({
		// 		method: "accounting.accounting.doctype.purchase_order.purchase_order.make_purchase_receipt",
		// 		frm: cur_frm
		// 	})
		// }, __("Create"));
		// frm.page.set_inner_btn_group_as_primary(__('Create'));
		
		cur_frm.add_custom_button(__("Purchase Receipt"), function() {
			get_doc(cur_frm.docname).then(
				function(result) { 
					frappe.model.with_doctype('Purchase Receipt', function() {
						var pr = frappe.model.get_new_doc('Purchase Receipt');
						pr.party = frm.doc.party;
						pr.company = frm.doc.company;
						pr.total_quantity = frm.doc.total_quantity;
						pr.total_amount = frm.doc.total_amount;
						result.forEach(function(item) {
							var pr_item = frappe.model.add_child(pr, 'items');
							pr_item.item = item.item;
							pr_item.qty = item.qty;
							pr_item.rate = item.rate;
							pr_item.amount = item.amount;
						});
						frappe.set_route('Form', 'Purchase Receipt', pr.name);
					});
				}
			);
		}, __("Create"));

		frm.page.set_inner_btn_group_as_primary(__('Create'));

		var get_doc = function(mydocname){
			var pr;
			return new Promise(function(resolve) {
				frappe.call({
					"method": "frappe.client.get",
					"args": {
						"doctype": "Purchase Order",
						"name": mydocname
					},
					"callback": function(response) {
						pr = response.message.items;   
						resolve(pr);
					}
				});
			});
		} 
	}
});

frappe.ui.form.on("Purchase Order Item", {
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
				frappe.model.set_value(cdt, cdn, 'schedule_date', frm.doc.schedule_date)
				frappe.model.set_value(cdt, cdn, 'rate', doc.standard_selling_rate)
			})
		}
	}
});
var calculate_total = function(frm, cdt, cdn) {
	var child = locals[cdt][cdn];
	frappe.model.set_value(cdt, cdn, "amount", child.qty * child.rate);
}


frappe.ui.form.on("Purchase Order Item", "qty", function(frm, cdt, cdn) {
	var purchase_item_details = frm.doc.items;
	var total = 0
	for(var i in purchase_item_details) {
		total = total + purchase_item_details[i].qty
	}
	frm.set_value("total_quantity", total)
});

frappe.ui.form.on("Purchase Order Item", "amount", function(frm, cdt, cdn) {
	var purchase_item_details = frm.doc.items;
	var total = 0
	for(var i in purchase_item_details) {
		total = total + purchase_item_details[i].amount
	}
	frm.set_value("total_amount", total)
});
