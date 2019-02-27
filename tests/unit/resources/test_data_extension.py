import uuid
import unittest
from tests import TestCase
from sfmc import client_factory, SearchFilter


class DataExtension(TestCase):

    def get_mc_client(self):
        creds = self.get_mc_credentials()
        client_factory.set_params(creds)

        return client_factory.make()

    def get_de_key(self):
        creds = self.get_mc_credentials()

        return creds.get('default_de_key')

    @unittest.skip('Need account with special rights')
    def test_create_data_extension(self):
        cl = self.get_mc_client()
        print(cl)
        self.assertTrue(False)

    @unittest.skip('Need account with special rights')
    def test_delete_data_extension(self):
        self.assertTrue(False)

    @unittest.skip('Need account with special rights')
    def test_add_additional_fields_to_data_extension(self):
        self.assertTrue(False)

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
        self.assertTrue(rows.status)

        # check row was added
        search_filter = SearchFilter.both(SearchFilter.equals('C_ID', c_id), SearchFilter.equals('C_EMAIL', c_email))

        rows = cl.DataExtensionRow.get(m_props=props, m_filter=search_filter)
        self.assertTrue(rows.status)
        self.assertEqual(rows.get_property('C_NAME'), c_name)

        # ########### update row
        c_name_updated = '{} updated'.format(c_name)
        props_values[2] = c_name_updated
        props_payload = {k: v for k, v in zip(props, props_values)}

        rows = cl.DataExtensionRow.update(props_payload)
        self.assertTrue(rows.status)
        # check that row had been updated
        rows = cl.DataExtensionRow.get(m_props=props, m_filter=search_filter)
        self.assertTrue(rows.status)
        self.assertEqual(rows.get_property('C_NAME'), c_name_updated)

        # ########### delete row
        rows = cl.DataExtensionRow.delete(props_payload)
        self.assertTrue(rows.status)
        rows = cl.DataExtensionRow.get(m_props=props, m_filter=search_filter)
        self.assertTrue(rows.status)
        self.assertTrue(rows.is_empty())
