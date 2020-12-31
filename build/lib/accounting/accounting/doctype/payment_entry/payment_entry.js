// Copyright (c) 2020, Shariq and contributors
// For license information, please see license.txt

frappe.ui.form.on('Payment Entry', {
	// refresh: function(frm) {

	// }
});

frappe.ui.form.on('Payment Entry', {
    onload(frm) {
        if(frm.parent.previousSibling.frm.doctype == 'Purchase Invoice'){
            frm.set_value('payment_type', 'Pay');
        }
        else if(frm.parent.previousSibling.frm.doctype == 'Sales Invoice'){
            frm.set_value('payment_type', 'Receive');
        }
    }
});