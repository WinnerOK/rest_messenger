from django.test import Client, TestCase
from rest_framework import status

client = Client()


class PingTest(TestCase):
    def test_ping(self):
        resp = client.get('/api/ping/')

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data, {"pong": True})
