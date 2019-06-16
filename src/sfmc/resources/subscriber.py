from sfmc.client import ResourceBase, ResourceHandler
from sfmc.resources.mixins import Gettable


class SubscriberResource(ResourceBase):
    """Resource wrapper for Subscriber entities"""
    pass


class SubscriberHandler(ResourceHandler, Gettable):
    """Subscriber handler"""
    resource_type = 'Subscriber'
    resource_base = SubscriberResource


class SubscriberSendResultResource(ResourceBase):
    """Resource wrapper for SubscriberSendResult entities"""
    pass


class SubscriberSendResultHandler(ResourceHandler, Gettable):
    """Subscriber handler"""
    resource_type = 'SubscriberSendResult'
    resource_base = SubscriberSendResultResource
