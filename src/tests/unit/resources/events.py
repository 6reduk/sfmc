import unittest
from tests import TestCase, ALLOW_BASED_ON_INTERNAL_CREDS_TESTS
from sfmc import ObjectDefinition


class BounceEventTestCase(TestCase):

    def test_describe(self):
        cl = self.get_mc_client()
        definition = cl.BounceEvent.describe()

        self.assertIsInstance(definition, ObjectDefinition)

    @unittest.skipUnless(ALLOW_BASED_ON_INTERNAL_CREDS_TESTS, "Do not allowed test based on internal data and creds")
    def test_get(self):
        cl = self.get_mc_client()
        resp = cl.BounceEvent.get()
        self.assertTrue(resp.is_valid)
        if len(resp.entities) > 0:
            self.assertTrue(resp.entities[0].ID)


class SentEventTestCase(TestCase):

    def test_describe(self):
        cl = self.get_mc_client()
        definition = cl.SentEvent.describe()
        self.assertIsInstance(definition, ObjectDefinition)

    @unittest.skipUnless(ALLOW_BASED_ON_INTERNAL_CREDS_TESTS, "Do not allowed test based on internal data and creds")
    def test_get(self):
        cl = self.get_mc_client()
        resp = cl.SentEvent.get()
        self.assertTrue(resp.is_valid)
        if len(resp.entities) > 0:
            self.assertTrue(resp.entities[0].SendID)


class SMSMTEventTestCase(TestCase):

    def test_describe(self):
        cl = self.get_mc_client()
        definition = cl.SMSMTEvent.describe()
        print(definition)
        self.assertIsInstance(definition, ObjectDefinition)

    @unittest.skipUnless(ALLOW_BASED_ON_INTERNAL_CREDS_TESTS, "Do not allowed test based on internal data and creds")
    def test_get(self):
        cl = self.get_mc_client()
        resp = cl.SMSMTEvent.get()
        print(resp)
        self.assertTrue(resp.is_valid)
        if len(resp.entities) > 0:
            self.assertTrue(resp.entities[0].SmsSendId)


class SMSMOEventTestCase(TestCase):

    def test_describe(self):
        cl = self.get_mc_client()
        definition = cl.SMSMOEvent.describe()
        self.assertIsInstance(definition, ObjectDefinition)

    @unittest.skipUnless(ALLOW_BASED_ON_INTERNAL_CREDS_TESTS, "Do not allowed test based on internal data and creds")
    def test_get(self):
        cl = self.get_mc_client()
        resp = cl.SMSMOEvent.get()
        self.assertTrue(resp.is_valid)
        if len(resp.entities) > 0:
            self.assertTrue(resp.entities[0].ObjectID)
