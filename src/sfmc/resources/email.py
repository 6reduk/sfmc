from sfmc.client import ResourceBase, ResourceHandler
from sfmc.resources.mixins import Gettable


class EmailResource(ResourceBase):
    """Resource wrapper for Email entities"""
    pass


class EmailHandler(ResourceHandler, Gettable):
    """Email handler"""
    resource_type = 'Email'
    resource_base = EmailResource
