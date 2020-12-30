# -*- coding: utf-8 -*-
# Copyright (c) 2020, Shariq and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class PurchaseInvoice(Document):
    def on_submit(self):
        self.balance_update(self.expense_account)
        self.balance_update(self.credit_to)
        self.make_gl_entry(self.expense_account, self.total_amount, 0)
        self.make_gl_entry(self.credit_to, 0, self.total_amount)

    def on_cancel(self):
        pass

    def balance_update(self, account):
        a = frappe.get_doc('Account', account)
        if a.account_type == 'Asset' or a.account_type == 'Expense':
            a.account_balance += self.total_amount
        elif a.account_type == 'Liability' or a.account_type == 'Income':
            a.account_balance -= self.total_amount
        a.save()

    def make_gl_entry(self, account, dr, cr):
        frappe.get_doc({
            'doctype': 'GL Entry',
            'posting_date': self.posting_date,
            'account': account,
            'debit_amount': dr,
            'credit_amount': cr,
            'voucher_type': self.doctype,
            'voucher_no': self.name,
            'party': self.party,
            'balance': frappe.db.get_value('Account', account, 'account_balance')
        }).insert()