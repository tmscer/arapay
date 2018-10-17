# Create your tests here.
from django.test import Client
from django.test import TestCase
from parameterized import parameterized

import payments.templatetags.payments_tags as tags
from payments.popo import InvoiceStats

client = Client(enforce_csrf_checks=True)


class EndpointTest(TestCase):
    @parameterized.expand([
        ('/', 302, {'Location': 'p/'}),
        ('/p/', 200, {}),
        ('/p/by_invoice/', 403, {}),
        ('/p/by_user/', 403, {}),
        ('/p/gen-var-sym/1/1/', 403, {})
    ])
    def test(self, path, expected_code, attrs):
        attrs.update({
            'Content-Type': 'text/html; charset=utf-8',
            'X-Frame-Options': 'SAMEORIGIN'
        })
        response = client.get(path)
        self.assertEqual(expected_code, response.status_code)
        for key, val in attrs.items():
            self.assertEqual(val, response[key])


class TemplateTagTest(TestCase):
    def test_get_item(self):
        item = tags.get_item({'one': 1, 'two': 2, 'three': 3}, 'two')
        self.assertEqual(2, item)


class PopoTest(TestCase):
    def test_invoice_stats(self):
        invoice_stats = InvoiceStats(invoice_id=0,
                                     total_users=[
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
