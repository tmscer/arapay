# Create your tests here.
from datetime import datetime as dt

from django.contrib.auth.models import User
from django.test import Client
from django.test import TestCase

import payments.templatetags.payments_tags as tags
from payments.models import Payment, Invoice, AccountInfo
from payments.popo import InvoiceStats

client = Client(enforce_csrf_checks=True)


class TemplateTagTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='me', email='me@example.com', password='1234')
        self.account_info = AccountInfo.objects.create(account_number=1111111112, bank_code='3030')
        self.invoice = Invoice.objects.create(name='cornflakes', amount_cents=200, date_deadline=dt.now(),
                                              account_info=self.account_info)
        self.payment = Payment.objects.create(invoice=self.invoice, user=self.user)

    def test_get_item(self):
        item = tags.get_item({'one': 1, 'two': 2, 'three': 3}, 'two')
        self.assertEqual(2, item)

    def test_make_tags(self):
        t = tags.make_tags('div', "one,two,three")
        self.assertEqual("<div>one</div><div>two</div><div>three</div>", t)

    def test_amount_owed(self):
        amount_cents = 300
        paid_amount_cents = 100
        owed_amount = tags.amount_owed(amount_cents, paid_amount_cents)
        self.assertEqual(2.0, owed_amount)

    def test_get_payment(self):
        payment = tags.get_payment(self.invoice, self.user.id)
        self.assertEqual(self.payment, payment)


class PopoTest(TestCase):
    def test_invoice_stats(self):
        invoice_stats = InvoiceStats(i=0,
                                     n_total=[
                                         {'name': 'me',
                                          'age': 20},
                                         {'name': 'you',
                                          'age': 20}
                                     ])
        invoice_stats.amount_cents_owed = 2 * 100
        invoice_stats.amount_cents_paid = 100
        invoice_stats.n_paid = 1
        invoice_stats.n_unpaid = 1
        self.assertEqual(50.0, invoice_stats.paid_percentage)
