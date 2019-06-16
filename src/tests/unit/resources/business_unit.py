import unittest
from tests import TestCase
from sfmc import ObjectDefinition


class BusinessUnitTestCase(TestCase):

    def test_describe(self):
        cl = self.get_mc_client()
        definition = cl.BusinessUnit.describe()

        self.assertIsInstance(definition, ObjectDefinition)

    @unittest.skip("Have no rights to get it")
    def test_get(self):
        cl = self.get_mc_client()
        resp = cl.BusinessUnit.get()

        self.assertTrue(resp.is_valid)
        if len(resp.entities) > 0:
            self.assertTrue(resp.entities[0].ID)
