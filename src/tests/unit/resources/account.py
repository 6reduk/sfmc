import unittest
from tests import TestCase
from sfmc import ObjectDefinition


class AccountTestCase(TestCase):

    def test_describe(self):
        cl = self.get_mc_client()
        definition = cl.Account.describe()
        self.assertIsInstance(definition, ObjectDefinition)

    @unittest.skip("Have no rights to get it")
    def test_get(self):
        cl = self.get_mc_client()
        resp = cl.Account.get()
        self.assertTrue(resp.is_valid)
        self.assertTrue(resp.entities[0].ID)
