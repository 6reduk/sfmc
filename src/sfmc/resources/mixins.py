from sfmc.resources.filter import SearchFilter
from sfmc.exceptions import ResourceHandlerException


class Gettable:
    def get(self, m_filter: SearchFilter = None, m_props: list = None, m_options: dict = None) -> 'ResourceBase':
        """
        Get data extensions
        :param m_filter:    filter
        :param m_props:     retrieve given props
        :param m_options:   additional options
        :return: ResourceBase
        """

        if m_props is None:
            try:
                m_props = self.describe().retrievable_property_names()
            except Exception as e:
                raise ResourceHandlerException('Can not describe object: {}'.format(e))

        if m_options is not None and type(m_options) is not dict:
            raise ResourceHandlerException('options must be a dict')

        resp = self.client.soap_get(self.get_resource_type(), m_filter, m_props, m_options)

        return self.make_resource(resp)
