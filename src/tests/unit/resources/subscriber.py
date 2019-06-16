import unittest
from tests import TestCase, ALLOW_BASED_ON_INTERNAL_CREDS_TESTS
from sfmc import ObjectDefinition


class SubscriberTestCase(TestCase):

    def test_describe(self):
        cl = self.get_mc_client()
        definition = cl.Subscriber.describe()

        self.assertIsInstance(definition, ObjectDefinition)

    @unittest.skipUnless(ALLOW_BASED_ON_INTERNAL_CREDS_TESTS, "Do not allowed test based on internal data and creds")
    def test_get(self):
        cl = self.get_mc_client()
        resp = cl.Subscriber.get()
        self.assertTrue(resp.is_valid)
        self.assertTrue(resp.entities[0].ID)


class SubscriberSendResultTestCase(TestCase):

    def test_describe(self):
        cl = self.get_mc_client()
        definition = cl.SubscriberSendResult.describe()

        self.assertIsInstance(definition, ObjectDefinition)

    @unittest.skipUnless(ALLOW_BASED_ON_INTERNAL_CREDS_TESTS, "Do not allowed test based on internal data and creds")
    def test_get(self):
        cl = self.get_mc_client()
        resp = cl.SubscriberSendResult.get()
        self.assertTrue(resp.is_valid)
        if len(resp.entities) > 0:
            self.assertTrue(resp.entities[0].ID)
