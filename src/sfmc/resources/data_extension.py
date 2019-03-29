from . import ResourceBase, ResourceHandler
from ..exceptions import ResourceHandlerException, ResourceMissingPropertyException
from .filter import SearchFilter


class DataExtensionResource(ResourceBase):
    """Data extension resource"""
    # TODO code logic
    pass


class DataExtensionHandler(ResourceHandler):
    """Data extension handler"""
    resource_type = 'DataExtension'
    resource_base = DataExtensionResource

    def get(self, m_filter: SearchFilter = None, m_props: list = None, m_options: dict = None) -> DataExtensionResource:
        """
        Get data extensions
        :param m_filter:    filter
        :param m_props:     retrieve given props
        :param m_options:   additional options
        :return: DataExtensionResource
        """

        if m_props is None:
            try:
                m_props = [prop.Name for prop in self.describe().retrievable_properties()]
            except Exception as e:
                raise ResourceHandlerException('Can not describe object: {}'.format(e))

        if m_options is not None and type(m_options) is not dict:
            raise ResourceHandlerException('options must be a dict')

        response = self.client.soap_get(self.get_resource_type(), m_filter, m_props, m_options)

        return DataExtensionResource.make_from_response(response)

    def name_for_customer_key(self, key: str) -> str:
        """
        Get data extension name for given key
        :param key: data extension key
        :return: de name
        """
        props = ["Name", "CustomerKey"]

        f = SearchFilter.equals('CustomerKey', key)

        response = self.client.soap_get(self.get_resource_type(), search_filter=f, props=props)

        d = DataExtensionResource.make_from_response(response)

        if d.status and len(d.results) == 1 and 'Name' in d.results[0]:
            return d.results[0]['Name']
        else:
            raise ResourceHandlerException('Unable to retrieve DataExtension name for customer key: {}'.format(key))

    def customer_key_for_name(self, name: str) -> str:
        """
        Get data extension key for given name
        :param name: data extension name
        :return: de key
        """
        props = ["Name", "CustomerKey"]

        f = SearchFilter.equals('Name', name)

        response = self.client.soap_get(self.get_resource_type(), search_filter=f, props=props)

        d = DataExtensionResource.make_from_response(response)

        if d.status and len(d.results) == 1 and 'CustomerKey' in d.results[0]:
            return d.results[0]['CustomerKey']
        else:
            raise ResourceHandlerException('Unable to retrieve DataExtension customer key for name: {}'.format(name))


class DataExtensionField(ResourceBase):
    def field_names(self) -> list:
        """List of field names"""
        return [f['Name'] for f in self.results]


class DataExtensionFieldHandler(ResourceHandler):
    resource_type = 'DataExtensionField'
    resource_base = DataExtensionField

    def __init__(self, client):
        self.customer_key = None
        super(DataExtensionFieldHandler, self).__init__(client)

    def set_customer_key(self, key):
        self.customer_key = key

        return self

    def get(self, customer_key=None, m_props=None):
        if customer_key is None:
            customer_key = self.customer_key

        if m_props is not None and type(m_props) is list:
            props = m_props
        else:
            try:
                props = [prop.Name for prop in self.describe().retrievable_properties()]
            except Exception as e:
                raise ResourceHandlerException('Can not describe object: {}'.format(e))

        f = SearchFilter.equals('DataExtension.CustomerKey', customer_key)

        response = self.client.soap_get(self.get_resource_type(), search_filter=f, props=props)

        return self.resource_base.make_from_response(response)


class DataExtensionRow(ResourceBase):

    def get_property(self, property_name):
        for p in self.properties()[0]:
            if p.Name == property_name:
                return p.Value

        raise ResourceMissingPropertyException('Property [{}] is missing in result set'.format(property_name))


class DataExtensionRowHandler(ResourceHandler):
    resource_type = 'DataExtensionObject'
    resource_base = DataExtensionRow

    def __init__(self, client):
        self.customer_key = None
        self.name = None
        super(DataExtensionRowHandler, self).__init__(client)

    @classmethod
    def get_resource_name(cls):
        return 'DataExtensionRow'

    def set_customer_key(self, key):
        self.customer_key = key

        return self

    def set_name(self, name):
        self.name = name

        return self

    def get(self, m_filter=None, m_props=None, m_options=None):
        res_type = "{}[{}]".format(self.get_resource_type(), self.name)
        response = self.client.soap_get(res_type, search_filter=m_filter, props=m_props, options=m_options)

        return self.make_resource_from_response(response)

    def _convert_props_to_service_scheme(self, customer_key, props):
        fields = []
        converted = {}

        for key, value in props.items():
            fields.append({"Name": key, "Value": value})

        converted['CustomerKey'] = customer_key
        converted['Properties'] = {}
        converted['Properties']['Property'] = fields

        return converted

    def _convert_props_to_service_scheme_for_delete(self, customer_key, props):
        fields = []
        converted = {}

        for key, value in props.items():
            fields.append({"Name": key, "Value": value})

        converted['CustomerKey'] = customer_key
        converted['Keys'] = {}
        converted['Keys']['Key'] = fields

        return converted

    def _prepare_properties_payload(self, props, customer_key, to_delete=False):
        customer_key = customer_key if customer_key is not None else self.customer_key

        props_converter = self._convert_props_to_service_scheme if to_delete is False else self._convert_props_to_service_scheme_for_delete

        if type(props) is list:
            payload_props = [props_converter(customer_key, i) for i in props]
        else:
            payload_props = props_converter(customer_key, props)

        return payload_props

    def add(self, props, customer_key=None):
        payload = self._prepare_properties_payload(props, customer_key)
        response = self.client.soap_post(self.get_resource_type(), payload)

        return self.make_resource_from_response(response)

    def update(self, props, customer_key=None):
        payload = self._prepare_properties_payload(props, customer_key)
        response = self.client.soap_patch(self.get_resource_type(), payload)

        return self.make_resource_from_response(response)

    def delete(self, props=None, customer_key=None):
        payload = self._prepare_properties_payload(props, customer_key, to_delete=True)
        response = self.client.soap_delete(self.get_resource_type(), payload)

        return self.make_resource_from_response(response)
