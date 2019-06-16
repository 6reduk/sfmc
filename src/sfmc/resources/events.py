from sfmc.client import ResourceBase, ResourceHandler
from sfmc.resources.mixins import Gettable


class BounceEventResource(ResourceBase):
    """Resource wrapper for BounceEvent entities"""
    pass


class BounceEventHandler(ResourceHandler, Gettable):
    """BounceEvent handler"""
    resource_type = 'BounceEvent'
    resource_base = BounceEventResource


class SentEventResource(ResourceBase):
    """Resource wrapper for SentEvent entities"""
    pass


class SentEventHandler(ResourceHandler, Gettable):
    """SentEvent handler"""
    resource_type = 'SentEvent'
    resource_base = SentEventResource


class SMSMTEventResource(ResourceBase):
    """Resource wrapper for SMSMTEvent entities"""
    pass


class SMSMTEventHandler(ResourceHandler, Gettable):
    """SMSMTEvent handler"""
    resource_type = 'SMSMTEvent'
    resource_base = SMSMTEventResource


class SMSMOEventResource(ResourceBase):
    """Resource wrapper for SMSMOEvent entities"""
    pass


class SMSMOEventHandler(ResourceHandler, Gettable):
    """SMSMOEvent handler"""
    resource_type = 'SMSMOEvent'
    resource_base = SMSMOEventResource
