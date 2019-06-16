import unittest
from tests import TestCase, ALLOW_BASED_ON_INTERNAL_CREDS_TESTS
from sfmc import ObjectDefinition


class SendTestCase(TestCase):

    def test_describe(self):
        cl = self.get_mc_client()
        definition = cl.Send.describe()

        self.assertIsInstance(definition, ObjectDefinition)

    @unittest.skipUnless(ALLOW_BASED_ON_INTERNAL_CREDS_TESTS, "Do not allowed test based on internal data and creds")
    def test_get(self):
        cl = self.get_mc_client()
        resp = cl.Send.get()
        self.assertTrue(resp.is_valid)
        self.assertTrue(resp.entities[0].ID)


class TriggeredSendDefinitionTestCase(TestCase):

    def test_describe(self):
        cl = self.get_mc_client()
        definition = cl.TriggeredSendDefinition.describe()
        self.assertIsInstance(definition, ObjectDefinition)

    @unittest.skipUnless(ALLOW_BASED_ON_INTERNAL_CREDS_TESTS, "Do not allowed test based on internal data and creds")
    def test_get(self):
        cl = self.get_mc_client()
        resp = cl.TriggeredSendDefinition.get()
        self.assertTrue(resp.is_valid)
        if len(resp.entities) > 0:
            self.assertTrue(resp.entities[0].Name)


class SMSTriggeredSendTestCase(TestCase):

    def test_describe(self):
        cl = self.get_mc_client()
        definition = cl.SMSTriggeredSend.describe()
        self.assertIsInstance(definition, ObjectDefinition)

    @unittest.skipUnless(ALLOW_BASED_ON_INTERNAL_CREDS_TESTS, "Do not allowed test based on internal data and creds")
    def test_get(self):
        cl = self.get_mc_client()
        resp = cl.SMSTriggeredSend.get()
        self.assertTrue(resp.is_valid)
        if len(resp.entities) > 0:
            self.assertTrue(resp.entities[0].SmsSendId)


class SMSTriggeredSendDefinitionTestCase(TestCase):

    def test_describe(self):
        cl = self.get_mc_client()
        definition = cl.SMSTriggeredSendDefinition.describe()
        self.assertIsInstance(definition, ObjectDefinition)

    @unittest.skipUnless(ALLOW_BASED_ON_INTERNAL_CREDS_TESTS, "Do not allowed test based on internal data and creds")
    def test_get(self):
        cl = self.get_mc_client()
        resp = cl.SMSTriggeredSendDefinition.get()
        self.assertTrue(resp.is_valid)
        if len(resp.entities) > 0:
            self.assertTrue(resp.entities[0].Name)


class SMSSharedKeywordTestCase(TestCase):

    def test_describe(self):
        cl = self.get_mc_client()
        definition = cl.SMSSharedKeyword.describe()
        self.assertIsInstance(definition, ObjectDefinition)

    @unittest.skipUnless(ALLOW_BASED_ON_INTERNAL_CREDS_TESTS, "Do not allowed test based on internal data and creds")
    def test_get(self):
        cl = self.get_mc_client()
        resp = cl.SMSSharedKeyword.get()
        self.assertTrue(resp.is_valid)
        if len(resp.entities) > 0:
            self.assertTrue(resp.entities[0].ShortCode)
