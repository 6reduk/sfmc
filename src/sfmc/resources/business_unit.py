from sfmc.client import ResourceBase, ResourceHandler
from sfmc.resources.mixins import Gettable


class BusinessUnitResource(ResourceBase):
    """Resource wrapper for BusinessUnit entities"""
    pass


class BusinessUnitHandler(ResourceHandler, Gettable):
    """BusinessUnit handler"""
    resource_type = 'BusinessUnit'
    resource_base = BusinessUnitResource
