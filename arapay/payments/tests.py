# Create your tests here.
from django.test import Client
from django.test import TestCase
from parameterized import parameterized

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
