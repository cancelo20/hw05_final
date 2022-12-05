from django.test import TestCase, Client
from ..constants import RESPONSE_COD_404


class ErrorViewsTest(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_error_page(self):
        response = self.guest_client.get('/no_name_page/')
        self.assertEqual(
            response.status_code,
            RESPONSE_COD_404,
            'status code должен быть 404')
