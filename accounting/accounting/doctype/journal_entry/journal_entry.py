# -*- coding: utf-8 -*-
# Copyright (c) 2020, Shariq and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import flt


class JournalEntry(Document):

    def validate(self):
        self.set_total_debit_credit()
        if self.difference:
            frappe.throw(_("Total Debit and Credit must be equal. The difference is {0}").format(self.difference))

    def set_total_debit_credit(self):
        self.total_debit, self.total_credit, self.difference = 0, 0, 0
        for a in self.accounting_entries:
            self.total_debit = flt(self.total_debit) + flt(a.debit)
            self.total_credit = flt(self.total_credit) + flt(a.credit)

        self.difference = flt(self.total_debit) - flt(self.total_credit)

    def on_submit(self):
        self.balance_update()
        self.make_gl_entry()

    def on_cancel(self):
        self.make_reverse_gl_entry(voucher_type = self.doctype, voucher_no = self.name)
        
    def make_reverse_gl_entry(voucher_type=None, voucher_no=None):
        pass

    def balance_update(self):
        for account in self.accounting_entries:
            a = frappe.get_doc('Account', account.account)
            if a.account_type == 'Asset' or a.account_type == 'Expense':
                if account.debit > 0:
                    a.account_balance += account.debit
                elif account.credit > 0:
                    a.account_balance -= account.credit
            elif a.account_type == 'Liability' or a.account_type == 'Income':
                if account.debit > 0:
                    a.account_balance -= account.debit
                elif account.credit > 0:
                    a.account_balance += account.credit
            a.save()

    def make_gl_entry(self):
        for account in self.accounting_entries:
            frappe.get_doc({
                'doctype': 'GL Entry',
                'posting_date': self.posting_date,
                'account': account.account,
                'debit_amount': account.debit,
                'credit_amount': account.credit,
                'voucher_type': self.doctype,
                'voucher_no': self.name,
                'party': account.party,
                'balance': frappe.db.get_value('Account', account.account, 'account_balance')
            }).insert()
