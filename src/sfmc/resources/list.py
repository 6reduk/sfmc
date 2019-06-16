from sfmc.client import ResourceBase, ResourceHandler
from sfmc.resources.mixins import Gettable


class ListResource(ResourceBase):
    """Resource wrapper for List entities"""
    pass


class ListHandler(ResourceHandler, Gettable):
    """Send handler"""
    resource_type = 'List'
    resource_base = ListResource
