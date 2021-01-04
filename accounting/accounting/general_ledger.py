from __future__ import unicode_literals
import frappe

def make_gl_entry(self, account, dr, cr):
	gl_entry = frappe.get_doc({
		'doctype': 'GL Entry',
		'posting_date': self.posting_date,
		'account': account,
		'debit_amount': dr,
		'credit_amount': cr,
		'voucher_type': self.doctype,
		'voucher_no': self.name,
		'party': self.party,
		'company': self.company
	})
	gl_entry.insert()

def make_reverse_gl_entry(voucher_type=None, voucher_no=None):
	gl_entries = frappe.get_all('GL Entry', filters={
								"voucher_type": voucher_type, "voucher_no": voucher_no}, fields=["*"])
	if gl_entries:
		cancel_gl_entry(gl_entries[0].voucher_type, gl_entries[0].voucher_no)

		for entry in gl_entries:
			debit = entry.debit_amount
			credit = entry.credit_amount
			entry.name = None
			entry.debit_amount = credit
			entry.credit_amount = debit
			entry.is_cancelled = 1
			entry.remarks = "Cancelled GL Entry (" + entry.voucher_no + ")"

			if entry.debit_amount or entry.credit_amount:
				make_cancelled_gl_entry(entry)

def make_cancelled_gl_entry(entry):
	gl_entry = frappe.new_doc('GL Entry')
	gl_entry.update(entry)
	gl_entry.insert()
	gl_entry.submit()

def cancel_gl_entry(voucher_type, voucher_no):
	frappe.db.sql("""UPDATE 
			`tabGL Entry` 
		SET 
			is_cancelled=1 
		WHERE 
			voucher_type=%s and voucher_no=%s and is_cancelled=0""",
		(voucher_type, voucher_no))

def get_account_balance(account):
	return frappe.db.sql("""SELECT 
					sum(debit_amount) - sum(credit_amount) 
				FROM 
					`tabGL Entry` 
				WHERE 
					is_cancelled=0 and account=%s""",
				(account))[0][0]
