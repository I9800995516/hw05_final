from http import HTTPStatus

from django.test import TestCase, Client


class StaticURLTests(TestCase):

    def setUp(self):
        self.guest_client = Client()

    def test_homepage(self):
        response_aa = self.guest_client.get('/about/author/')
        response_at = self.guest_client.get('/about/tech/')
        self.assertEqual(response_aa.status_code, HTTPStatus.OK.value)
        self.assertEqual(response_at.status_code, HTTPStatus.OK.value)
