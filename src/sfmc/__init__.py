import logging
from sfmc.client import Client, ClientFactory, ObjectDefinition, ObjectDefinitionProperty, ResourceBase, ResourceHandler
from sfmc.resources.data_extension import DataExtensionHandler, DataExtensionRowHandler, DataExtensionFieldHandler
from sfmc.resources.subscriber import SubscriberHandler, SubscriberSendResultHandler
from sfmc.resources.send import SendHandler, TriggeredSendDefinitionHandler, SMSTriggeredSendHandler, \
    SMSTriggeredSendDefinitionHandler, SMSSharedKeywordHandler
from sfmc.resources.email import EmailHandler
from sfmc.resources.events import BounceEventHandler, SentEventHandler, SMSMTEventHandler, SMSMOEventHandler
from sfmc.resources.business_unit import BusinessUnitHandler
from sfmc.resources.list import ListHandler
from sfmc.resources.account import AccountHandler
from sfmc.resources.filter import SearchFilter

logger_debug = logging.getLogger('sfmc')
logger_debug.setLevel(logging.DEBUG)

client_factory = ClientFactory()

handlers = [
    DataExtensionHandler,
    DataExtensionRowHandler,
    DataExtensionFieldHandler,
    SubscriberHandler,
    SubscriberSendResultHandler,
    SendHandler,
    TriggeredSendDefinitionHandler,
    SMSTriggeredSendHandler,
    SMSTriggeredSendDefinitionHandler,
    SMSSharedKeywordHandler,
    EmailHandler,
    BounceEventHandler,
    SentEventHandler,
    SMSMTEventHandler,
    SMSMOEventHandler,
    BusinessUnitHandler,
    ListHandler,
    AccountHandler
]

# Bind all available resource handlers
client_factory.bind_resources(handlers)
