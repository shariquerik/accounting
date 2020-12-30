// Copyright (c) 2020, Shariq and contributors
// For license information, please see license.txt

frappe.ui.form.on('Purchase Invoice', {
	// refresh: function(frm) {

	// }
});

frappe.ui.form.on("Purchase Invoice Item", {
	qty: function(frm,cdt, cdn){
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


frappe.ui.form.on("Purchase Invoice Item", "qty", function(frm, cdt, cdn) {
    var purchase_item_details = frm.doc.item;
    var total = 0
    for(var i in purchase_item_details) {
        total = total + purchase_item_details[i].qty
    }
    frm.set_value("total_quantity", total)
});

frappe.ui.form.on("Purchase Invoice Item", "amount", function(frm, cdt, cdn) {
    var purchase_item_details = frm.doc.item;
    var total = 0
    for(var i in purchase_item_details) {
        total = total + purchase_item_details[i].amount
    }
    frm.set_value("total_amount", total)
});