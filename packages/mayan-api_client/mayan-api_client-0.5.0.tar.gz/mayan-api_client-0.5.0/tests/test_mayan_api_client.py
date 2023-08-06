from __future__ import unicode_literals

import unittest2 as unittest

from mayan_api_client import API
from mayan_api_client import exceptions


class TestAPI(API):
    def __init__(self, *args, **kwargs):
        pass


class APITestCase(unittest.TestCase):
    def setUp(self):
        self.api = TestAPI()

    def test_get_apps(self):
        self.api._apps = ['test_app']

        self.assertEqual(self.api._apps, ['test_app'])

    def test_wrong_get_apps(self):
        self.api._apps = ['test_app']

        with self.assertRaises(exceptions.UnknownAppError):
            self.api.wrong_app.resource.get()
