// Copyright (c) 2020, Shariq and contributors
// For license information, please see license.txt

frappe.ui.form.on('Party', {
	// refresh: function(frm) {
	
	// }
});

frappe.ui.form.on("Party", "party_type", function (frm, cdt, cdn) {
	if (frm.doc.party_type == "Supplier"){ 
		frm.set_value('naming_series', 'SUP-.YYYY.-');
	} 
	else{ 
		frm.set_value('naming_series', 'CUST-.YYYY.-');
	} 
	frm.refresh_field('naming_series');
})
