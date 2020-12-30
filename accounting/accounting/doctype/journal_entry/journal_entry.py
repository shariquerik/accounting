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
            frappe.throw(_("Total Debit and Credit must be equal. The difference is {0}").format(
                self.difference))

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
        self.ignore_linked_doctypes = ('GL Entry')
        self.make_reverse_gl_entry(voucher_type=self.doctype, voucher_no=self.name)

    def make_reverse_gl_entry(self, voucher_type=None, voucher_no=None):
        gl_entries = frappe.get_all('GL Entry', filters={"voucher_type": voucher_type, "voucher_no": voucher_no}, fields=["*"])
        if gl_entries:
            self.cancel_gl_entry(gl_entries[0].voucher_type, gl_entries[0].voucher_no)
            self.adjust_account_balance()

            for entry in gl_entries:
                debit = entry.debit_amount
                credit = entry.credit_amount
                entry.name = None
                entry.debit_amount = credit
                entry.credit_amount = debit
                entry.is_cancelled = 1
                entry.remarks = "Cancelled GL Entry ("+ entry.voucher_no +")"
                entry.balance= frappe.db.get_value('Account', entry.account, 'account_balance')
                
                if entry.debit_amount or entry.credit_amount:
                    self.make_cancelled_gl_entry(entry)

    def make_cancelled_gl_entry(self, entry):
        gl = frappe.new_doc('GL Entry')
        gl.update(entry)
        gl.insert()
        gl.submit()

    def cancel_gl_entry(self, voucher_type, voucher_no):
        frappe.db.sql("""UPDATE `tabGL Entry` SET is_cancelled=1 WHERE voucher_type=%s and voucher_no=%s and is_cancelled=0""",
                      (voucher_type, voucher_no))

    def adjust_account_balance(self):
        for account in self.accounting_entries:
            a = frappe.get_doc('Account', account.account)
            if a.account_type == 'Asset' or a.account_type == 'Expense':
                if account.debit > 0:
                    a.account_balance -= account.debit
                elif account.credit > 0:
                    a.account_balance += account.credit
            elif a.account_type == 'Liability' or a.account_type == 'Income':
                if account.debit > 0:
                    a.account_balance += account.debit
                elif account.credit > 0:
                    a.account_balance -= account.credit
            a.save()

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
