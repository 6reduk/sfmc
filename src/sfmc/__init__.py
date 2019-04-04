import logging
from .client import Client, ClientFactory, ObjectDefinition, ObjectDefinitionProperty, ResourceBase, ResourceHandler
from .resources.data_extension import DataExtensionHandler, DataExtensionRowHandler, DataExtensionFieldHandler
from .resources.filter import SearchFilter


logger_debug = logging.getLogger('sfmc')
logger_debug.setLevel(logging.DEBUG)

client_factory = ClientFactory()

# Bind all available resource handlers
client_factory.bind_resource(DataExtensionHandler)\
    .bind_resource(DataExtensionRowHandler)\
    .bind_resource(DataExtensionFieldHandler)
