from sfmc.client import ResourceBase, ResourceHandler
from sfmc.resources.mixins import Gettable


class SendResource(ResourceBase):
    """Resource wrapper for Send entities"""
    pass


class SendHandler(ResourceHandler, Gettable):
    """Send handler"""
    resource_type = 'Send'
    resource_base = SendResource


class TriggeredSendDefinitionResource(ResourceBase):
    """Resource wrapper for TriggeredSendDefinition entities"""
    pass


class TriggeredSendDefinitionHandler(ResourceHandler, Gettable):
    """TriggeredSendDefinition handler"""
    resource_type = 'TriggeredSendDefinition'
    resource_base = TriggeredSendDefinitionResource


class SMSTriggeredSendResource(ResourceBase):
    """Resource wrapper for SMSTriggeredSend entities"""
    pass


class SMSTriggeredSendHandler(ResourceHandler, Gettable):
    """SMSTriggeredSend handler"""
    resource_type = 'SMSTriggeredSend'
    resource_base = SMSTriggeredSendResource


class SMSTriggeredSendDefinitionResource(ResourceBase):
    """Resource wrapper for SMSTriggeredSendDefinition entities"""
    pass


class SMSTriggeredSendDefinitionHandler(ResourceHandler, Gettable):
    """SMSTriggeredSendDefinition handler"""
    resource_type = 'SMSTriggeredSendDefinition'
    resource_base = SMSTriggeredSendDefinitionResource


class SMSSharedKeywordResource(ResourceBase):
    """Resource wrapper for SMSSharedKeyword entities"""
    pass


class SMSSharedKeywordHandler(ResourceHandler, Gettable):
    """SMSTriggeredSendDefinition handler"""
    resource_type = 'SMSSharedKeyword'
    resource_base = SMSSharedKeywordResource
