from sfmc.client import ResourceBase, ResourceHandler
from sfmc.resources.mixins import Gettable


class AccountResource(ResourceBase):
    """Resource wrapper for Account entities"""
    pass


class AccountHandler(ResourceHandler, Gettable):
    """Account handler"""
    resource_type = 'Account'
    resource_base = AccountResource
