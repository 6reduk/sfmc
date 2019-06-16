import uuid
import unittest
from tests import TestCase, INCLUDE_LONG_TESTS
from sfmc import SearchFilter


class DETestCase(TestCase):

    def get_de_key(self) -> str:
        creds = self.get_mc_credentials()

        return creds.get('default_de_key')


class DEField(DETestCase):

    def test_get_fields(self):
        cl = self.get_mc_client()
        cl.DataExtensionField.set_customer_key(self.get_de_key())
        res = cl.DataExtensionField.get()
        d = [e.Name for e in res.entities]
        self.assertEqual(['C_ID', 'C_NAME', 'C_EMAIL'], d)


class DataExtensionRowTest(DETestCase):
    def test_add_update_delete_row(self):
        props = ['C_ID', 'C_EMAIL', 'C_NAME']

        c_id = str(uuid.uuid4())
        c_email = '{}@gmail.com'.format(c_id)
        c_name = 'Test value for {}'.format(c_id)
        props_values = [c_id, c_email, c_name]
        props_payload = {k: v for k, v in zip(props, props_values)}

        cl = self.get_mc_client()
        de_name = cl.DataExtension.name_for_customer_key(self.get_de_key())
        cl.DataExtensionRow.set_customer_key(self.get_de_key()).set_name(de_name)

        # ########### add row to data extension
        rows = cl.DataExtensionRow.add(props_payload)
        self.assertTrue(rows.is_valid)

        # check row was added
        search_filter = SearchFilter.both(SearchFilter.equals('C_ID', c_id), SearchFilter.equals('C_EMAIL', c_email))

        rows = cl.DataExtensionRow.get(m_props=props, m_filter=search_filter)
        self.assertTrue(rows.is_valid)
        self.assertTrue(rows.entities_count == 1)
        self.assertEqual(rows.entities[0].get_property_value('C_NAME'), c_name)

        # ########### update row
        c_name_updated = '{} updated'.format(c_name)
        props_values[2] = c_name_updated
        props_payload = {k: v for k, v in zip(props, props_values)}

        rows = cl.DataExtensionRow.update(props_payload)
        self.assertTrue(rows.is_valid)
        # check that row had been updated
        rows = cl.DataExtensionRow.get(m_props=props, m_filter=search_filter)
        self.assertTrue(rows.is_valid)
        self.assertEqual(rows.entities[0].get_property_value('C_NAME'), c_name_updated)

        # ########### delete row
        rows = cl.DataExtensionRow.delete(props_payload)
        self.assertTrue(rows.is_valid)
        rows = cl.DataExtensionRow.get(m_props=props, m_filter=search_filter)
        self.assertTrue(rows.is_valid)
        self.assertTrue(rows.is_empty)

    @unittest.skipUnless(INCLUDE_LONG_TESTS, 'Too long test execution')
    def test_get_more_available_results(self):
        props = ['C_ID', 'C_EMAIL', 'C_NAME']
        props_values = []
        for i in range(2600):
            c_id = str(uuid.uuid4())
            c_email = '{}@gmail.com'.format(c_id)
            c_name = 'Test value for {}'.format(c_id)
            props_values.append((c_id, c_email, c_name))

        props_payload = []
        for p in props_values:
            props_payload.append({k: v for k, v in zip(props, p)})

        cl = self.get_mc_client()
        de_name = cl.DataExtension.name_for_customer_key(self.get_de_key())  # get data without de name is impossible
        cl.DataExtensionRow.set_customer_key(self.get_de_key()).set_name(de_name)

        cl.DataExtensionRow.add(props_payload)
        resp = cl.DataExtensionRow.get(m_props=props)
        self.assertTrue(resp.is_valid)
        r1 = resp.entities[0]
        self.assertTrue(resp.has_more_results)
        resp = resp.get_more_results()
        r2 = resp.entities[0]
        self.assertNotEqual(getattr(r1, 'C_ID'), getattr(r2, 'C_ID'))

        # resp = cl.DataExtensionRow.get(m_props=props)
        # for e in resp:
        #     cl.DataExtensionRow.delete(e.payload())

        # cleanup
        for p in props_payload:
            cl.DataExtensionRow.delete(p)


class DataExtension(DETestCase):
    @unittest.skip('Need account with special rights')
    def test_create_data_extension(self):
        self.assertTrue(False)

    @unittest.skip('Need account with special rights')
    def test_delete_data_extension(self):
        self.assertTrue(False)

    @unittest.skip('Need account with special rights')
    def test_add_additional_fields_to_data_extension(self):
        self.assertTrue(False)
