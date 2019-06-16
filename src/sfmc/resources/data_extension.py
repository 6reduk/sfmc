from typing import List, Mapping, Any, Union
from sfmc.client import ResourceBase, ResourceHandler, Entity
from sfmc.exceptions import ResourceHandlerException
from sfmc.resources.filter import SearchFilter
from sfmc.resources.mixins import Gettable


class DataExtensionResource(ResourceBase):
    """Resource wrapper for DataExtension entities"""
    pass


class DataExtensionHandler(ResourceHandler, Gettable):
    """Data extension handler"""
    resource_type = 'DataExtension'
    resource_base = DataExtensionResource

    def name_for_customer_key(self, key: str) -> str:
        """
        Get data extension name for given key
        :param key: data extension key
        :return: de name
        """
        props = ["Name", "CustomerKey"]

        f = SearchFilter.equals('CustomerKey', key)

        res = self.get(m_filter=f, m_props=props)

        if not res.is_valid:
            msg = 'Can not determine name for key{}: invalid service response[{}]'.format(key, res)
            raise ResourceHandlerException(msg)

        if res.is_empty:
            msg = 'Can not determine name for key[{}]:result set is empty, resource: {}'.format(key, res)
            raise ResourceHandlerException(msg)

        return res.entities[0].Name

    def customer_key_for_name(self, name: str) -> str:
        """
        Get data extension key for given name
        :param name: data extension name
        :return: de key
        """
        props = ["Name", "CustomerKey"]

        f = SearchFilter.equals('Name', name)

        res = self.get(m_filter=f, m_props=props)

        if not res.is_valid:
            msg = 'Can not determine key for name{}: invalid service response[{}]'.format(name, res)
            raise ResourceHandlerException(msg)

        if res.is_empty:
            msg = 'Can not determine key for name[{}]:result set is empty, resource: {}'.format(name, res)
            raise ResourceHandlerException(msg)

        return res.entities[0].CustomerKey


class DataExtensionField(ResourceBase):
    """Resource wrapper for data extension field entities"""
    pass


class DataExtensionFieldHandler(ResourceHandler):
    """Data extension field handler"""
    resource_type = 'DataExtensionField'
    resource_base = DataExtensionField

    def __init__(self, client):
        self.customer_key: str = None
        super(DataExtensionFieldHandler, self).__init__(client)

    def set_customer_key(self, key: str) -> 'DataExtensionFieldHandler':
        self.customer_key = key

        return self

    def get(self, customer_key: str = None, m_props: List[str] = None) -> ResourceBase:
        if customer_key is None:
            customer_key = self.customer_key

        if m_props is not None and type(m_props) is list:
            props = m_props
        else:
            try:
                props = self.describe().retrievable_property_names()
            except Exception as e:
                raise ResourceHandlerException('Can not describe object: {}'.format(e))

        f = SearchFilter.equals('DataExtension.CustomerKey', customer_key)

        res = self.client.soap_get(self.get_resource_type(), search_filter=f, props=props)

        return self.make_resource(res)


class DataExtensionRowEntity(Entity):

    def __getattr__(self, item) -> Any:
        if item == 'Properties':
            if not self.has_properties():
                raise AttributeError('No such attribute [{}]'.format(item))
            return self.get_properties()

        if item in self.properties:
            return self.properties[item].Value

        if item not in self.data:
            raise AttributeError('No such attribute [{}]'.format(item))

        return self.data[item]

    def payload(self):
        return {p.Name: p.Value for p in self.properties.values()}


class DataExtensionRow(ResourceBase):
    """Resource wrapper for data extension row entities"""
    entity_factory = DataExtensionRowEntity


class DataExtensionRowHandler(ResourceHandler):
    """Data extension row handler"""
    resource_type = 'DataExtensionObject'
    resource_name = 'DataExtensionRow'
    resource_base = DataExtensionRow

    def __init__(self, client):
        self.customer_key: str = None
        self.name: str = None
        super(DataExtensionRowHandler, self).__init__(client)

    def set_customer_key(self, key: str) -> 'DataExtensionRowHandler':
        self.customer_key = key

        return self

    def set_name(self, name: str) -> 'DataExtensionRowHandler':
        self.name = name

        return self

    def get(self, m_filter: SearchFilter = None, m_props: List[str] = None,
            m_options: Mapping[str, Any] = None) -> ResourceBase:
        """Get data extension rows(objects)"""
        res_type = "{}[{}]".format(self.get_resource_type(), self.name)

        resp = self.client.soap_get(res_type, search_filter=m_filter, props=m_props, options=m_options)

        return self.make_resource(resp)

    def _convert_props_to_scheme(self, customer_key: str, props: Mapping[str, Any]) -> Mapping[str, Any]:
        fields = []
        converted = {}

        for key, value in props.items():
            fields.append({"Name": key, "Value": value})

        converted['CustomerKey'] = customer_key
        converted['Properties'] = {}
        converted['Properties']['Property'] = fields

        return converted

    def _convert_props_to_scheme_for_delete(self, customer_key: str, props: Mapping[str, Any]) -> Mapping[str, Any]:
        fields = []
        converted = {}

        for key, value in props.items():
            fields.append({"Name": key, "Value": value})

        converted['CustomerKey'] = customer_key
        converted['Keys'] = {}
        converted['Keys']['Key'] = fields

        return converted

    def _prepare_properties_payload(self, props: Union[Mapping[str, Any], List[Mapping[str, Any]]], customer_key: str,
                                    to_delete: bool = False) -> Union[Mapping[str, Any], List[Mapping[str, Any]]]:
        customer_key = customer_key if customer_key is not None else self.customer_key

        props_converter = self._convert_props_to_scheme if to_delete is False else self._convert_props_to_scheme_for_delete

        if type(props) is list:
            payload_props = [props_converter(customer_key, i) for i in props]
        else:
            payload_props = props_converter(customer_key, props)

        return payload_props

    def add(self, props: Union[Mapping[str, Any], List[Mapping[str, Any]]], customer_key: str = None) -> ResourceBase:
        """
        Create new rows with given props
        :param props:   Single object properties or list of object properties
        :param customer_key:    customer key
        :return: resource
        """
        customer_key = customer_key if customer_key is not None else self.customer_key
        payload = self._prepare_properties_payload(props, customer_key)
        resp = self.client.soap_post(self.get_resource_type(), payload)

        return self.make_resource(resp)

    def update(self, props: Union[Mapping[str, Any], List[Mapping[str, Any]]],
               customer_key: str = None) -> ResourceBase:
        """
        Update rows with given properties. Objects will found by index property
        :param props:   Single object properties or list of object properties
        :param customer_key:    customer key
        :return: resource
        """
        customer_key = customer_key if customer_key is not None else self.customer_key
        payload = self._prepare_properties_payload(props, customer_key)
        resp = self.client.soap_patch(self.get_resource_type(), payload)

        return self.make_resource(resp)

    def delete(self, props: Union[Mapping[str, Any], List[Mapping[str, Any]]] = None,
               customer_key: str = None) -> ResourceBase:
        """
        Delete objects
        :param props: Single object properties or list of object properties
        :param customer_key: customer key
        :return: resource
        """
        customer_key = customer_key if customer_key is not None else self.customer_key
        payload = self._prepare_properties_payload(props, customer_key, to_delete=True)
        resp = self.client.soap_delete(self.get_resource_type(), payload)

        return self.make_resource(resp)
