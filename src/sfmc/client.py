import os
import os.path
import pathlib
import time
import datetime
import json
import logging
from typing import Mapping, Any, Dict, List, Iterable, Callable, MutableMapping

import requests
from suds.client import Client as SoapClient
from suds.wsse import Security, UsernameToken
from suds.sax.element import Element

from sfmc.exceptions import (ConfigureError, AuthenticationError, APIRequestError, SOAPRequestError,
                             ResourceMissingPropertyException, NoMoreDataAvailable, ResourceHandlerException)
from sfmc.util import check_required_keys, all_keys_not_none, any_keys_not_none, suds_results_to_simple_types
from sfmc.resources.filter import SearchFilter

DEFAULT_USER_AGENT = 'sfmc'
DEFAULT_AUTH_URL = 'https://auth.exacttargetapis.com/v1/requestToken?legacy=1'
DEFAULT_WSDL_URL = 'https://webservice.exacttarget.com/etframework.wsdl'
DEFAULT_WSDL_FILE_EXPIRE_TIME = 60 * 60 * 24  # 1 day in seconds


class Authenticator:
    """Provide authentication"""

    def __init__(self, client_id: str, client_secret: str, auth_url: str = DEFAULT_AUTH_URL,
                 user_agent: str = DEFAULT_USER_AGENT):
        """
           :param auth_url: Authorization url
           :param client_id: client id
           :param client_secret: client secret
           :param user_agent: user agent
           :return:
           """
        self.auth_url = auth_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.user_agent = user_agent

        self.endpoint = None
        self.auth_token_expiration = None
        self.auth_legacy_token = None
        self.auth_refresh_token = None
        self.appsignature = None
        self.auth_token = None
        self.last_refresh_ts = time.time()
        self.refresh_delay = 60 * 10  # 10 minutes

    def refresh(self, force=False):
        if self.auth_expired() or force:
            self.refresh_token()

        if self.endpoint is None or force:
            self.detect_endpoint()

    def refresh_token(self):
        """
            Refresh auth token
            :param auth_url: Authorization url
            :param client_id: client id
            :param client_secret: client secret
            :param refresh_token: refresh token if exists
            :param user_agent: user agent
            :return:
            """
        headers = {'content-type': 'application/json', 'user-agent': self.user_agent}

        payload = {
            'clientId': self.client_id,
            'clientSecret': self.client_secret,
            'accessType': 'offline'
        }

        if self.auth_refresh_token is not None:
            payload['refreshToken'] = self.auth_refresh_token

        res = requests.post(self.auth_url, headers=headers, data=json.dumps(payload))
        if res.status_code != 200:
            raise AuthenticationError('Authorization failed: ' + repr(res))

        response_body = res.json()
        if 'accessToken' not in response_body:
            raise Exception('Unable to validate provided pair client_id/client_secret):' + repr(response_body))

        self.auth_token = response_body['accessToken']
        self.auth_token_expiration = time.time() + response_body['expiresIn']
        self.auth_legacy_token = response_body['legacyToken']
        self.auth_refresh_token = response_body['refreshToken'] if 'refreshToken' in response_body else None

    def detect_endpoint(self):
        """
            Detect soap-service end point
            """
        url = 'https://www.exacttargetapis.com/platform/v1/endpoints/soap?access_token=' + self.auth_token
        headers = {'user-agent': self.user_agent}

        try:
            res = requests.get(url, headers)
            response_body = res.json()
            if 'url' in response_body:
                self.endpoint = str(response_body['url'])
        except Exception as e:
            raise APIRequestError('Unable to determine endpoints stack: ' + str(e))

    def auth_expired(self) -> bool:
        """
        Check auth token expiration
        :return: is expired
        """
        if self.auth_token is None:
            return True

        if self.auth_token_expiration is None or self.auth_token_expiration < time.time() + 300:
            return True

        if self.last_refresh_ts + self.refresh_delay < time.time():
            return True

        return False


class SoapClientFactory:
    def __init__(self, local_path: str = None, url: str = DEFAULT_WSDL_URL,
                 local_file_expire_time=DEFAULT_WSDL_FILE_EXPIRE_TIME,
                 debug=False):
        self.local_path = local_path
        self.url = url
        self.local_file_expire_time = local_file_expire_time
        self.debug = debug
        self._local_url = None
        self._client = None

    def _download(self, url, local_path):
        """
        Download wsdl file
        :param wsdl_url:        url where file located
        :param local_path:      full qualified path where store file
        :return:
        """
        # check path
        p = pathlib.Path(os.path.dirname(local_path))
        if not p.exists():
            p.mkdir(parents=True)

        with open(local_path, 'w') as of:
            r = requests.get(url)
            of.write(r.text)

    def _local_wsdl_is_expired(self, local_path: str) -> bool:
        """
        Check wsdl file expiration
        :param local_path:      path to wsdl file
        :return:
        """
        ts = time.mktime(time.gmtime(os.path.getmtime(local_path)))
        d = time.mktime(datetime.datetime.now().timetuple())

        return ts + self.local_file_expire_time < d

    def fetch_wsdl(self):
        """
        Retrieve and store wsdl file
        """
        if not os.path.exists(self.local_path) \
                or os.path.getsize(self.local_path) == 0 \
                or self._local_wsdl_is_expired(self.local_path):
            self._download(self.url, self.local_path)
        self._local_url = 'file:///' + self.local_path

    def init(self):
        self.fetch_wsdl()

    def make(self, authenticator: Authenticator):
        """Build and configure soap client"""
        if self._client is None:
            self._client = SoapClient(self._local_url, faults=False, cachingpolicy=0)

            if self.debug:
                logging.basicConfig(level=logging.INFO)
                logging.getLogger('suds.client').setLevel(logging.DEBUG)
                logging.getLogger('suds.transport').setLevel(logging.DEBUG)
                logging.getLogger('suds.xsd.schema').setLevel(logging.DEBUG)
                logging.getLogger('suds.wsdl').setLevel(logging.DEBUG)
            else:
                logging.getLogger('suds').setLevel(logging.INFO)

        # FIXME
        # Need make copy by suds.client.clone() method,
        # but now got this issue https://bitbucket.org/jurko/suds/issues/7/recursion-depth-reached
        # cl = self._client.clone()

        cl = self._client

        cl.set_options(location=authenticator.endpoint)

        security = Security()
        token = UsernameToken('*', '*')
        security.tokens.append(token)
        cl.set_options(wsse=security)

        element_oauth = Element('oAuth', ns=('etns', 'http://exacttarget.com'))
        element_oauth_token = Element('oAuthToken').setText(authenticator.auth_legacy_token)
        element_oauth.append(element_oauth_token)
        cl.set_options(soapheaders=[element_oauth])

        return cl


class Response:
    """Exact Service response wrapper"""

    def __init__(self):
        self.raw_response = None
        self.code = None
        self.status = False
        self.message = None
        self.more_results = False
        self.request_id = None
        self.results = []
        self.valid_response = False

    @classmethod
    def make_from_service_response(cls, resp, is_rest: bool = False) -> 'Response':
        """
        Build resource from soap-service response
        :param resp:        service soap/rest response
        :param is_rest:     indicate rest request
        """
        code = None
        status = False
        message = None
        more_results = False
        request_id = None
        results = []

        if resp is None:
            return cls()

        if is_rest:
            code = resp.status_code
            status = True if code == 200 else False
            results = resp.json()
        else:  # soap call
            code = resp[0]  # suds puts the code in tuple position 0
            body = resp[1]  # and the result in tuple position 1

            if body and 'RequestID' in body:
                request_id = body['RequestID']

            if code == 200:
                status = True

                if 'OverallStatus' in body:
                    message = body['OverallStatus']
                    if body['OverallStatus'] == "MoreDataAvailable":
                        more_results = True
                    elif body['OverallStatus'] != "OK":
                        status = False

                body_container_tag = None
                if 'Results' in body:  # most SOAP responses are wrapped in 'Results'
                    body_container_tag = 'Results'
                elif 'ObjectDefinition' in body:  # Describe SOAP response is in 'ObjectDefinition'
                    body_container_tag = 'ObjectDefinition'

                if body_container_tag is not None:
                    results = body[body_container_tag]

        inst = cls()
        inst.raw_response = resp
        inst.code = code
        inst.status = status
        inst.message = message
        inst.more_results = more_results
        inst.request_id = request_id
        inst.results = results
        inst.valid_response = True

        return inst

    @property
    def is_valid(self) -> bool:
        return self.valid_response and self.status

    @property
    def is_empty(self) -> bool:
        return len(self.results) == 0

    def __repr__(self):
        msg = '{}[valid:{},code:{},status:{},message:{},more_results:{},request_id:{},results:{}]'
        return msg.format(self.__class__.__name__, self.valid_response, self.code, self.status, self.message,
                          self.more_results, self.request_id, suds_results_to_simple_types(self.results))


class Client:
    """Sales Force client.
    Call resource handlers dynamically based on their name:
    client.some_resource.action(args, kwargs)
    """

    def __init__(self):
        self.authenticator: Authenticator = None
        self.soap_client_factory: SoapClientFactory = None
        self.soap_client = None
        self.resource_handlers_map = {}
        self.resource_handlers = {}

    def refresh(self, force: bool = False):
        """
        Prepare client to work
        """
        self.authenticator.refresh(force)
        self.soap_client = self.soap_client_factory.make(self.authenticator)

    def __getattr__(self, item: str) -> 'ResourceHandler':
        if item not in self.resource_handlers_map:
            raise LookupError('Missing handler for resource ' + item)

        if item not in self.resource_handlers:
            self.resource_handlers[item] = self.resource_handlers_map[item](self)

        return self.resource_handlers[item]

    def soap_describe_object(self, obj_type: str) -> Response:
        """
        Get object definition
        :param obj_type: Resource type described at wsdl
        :return:
        """
        self.authenticator.refresh()

        request = self.soap_client.factory.create('ArrayOfObjectDefinitionRequest')

        obj_definition = {'ObjectType': obj_type}
        request.ObjectDefinitionRequest = [obj_definition]

        resp = self.soap_client.service.Describe(request)

        if resp is None:
            raise SOAPRequestError('Empty response for describe request for {} object type'.format(obj_type))

        return Response.make_from_service_response(resp)

    def soap_get(self, obj_type: str, search_filter: SearchFilter = None, props: list = None,
                 options: dict = None) -> Response:
        """
        Get single object or array of objects by soap request
        :param obj_type: requested object type
        :param search_filter: search filter
        :param props: requested object fields
        :param options: additional request option
        :return: service response
        """
        self.authenticator.refresh()

        request = self.soap_client.factory.create('RetrieveRequest')

        request.ObjectType = obj_type

        if props is None:
            props = []
        elif type(props) is not list:
            raise TypeError('props must be list of property names or None')

        request.Properties = props

        if search_filter is not None:
            if not isinstance(search_filter, SearchFilter):
                raise TypeError('search_filter must be an {} instance'.format(SearchFilter.__class__.__name__))

            filter_payload = search_filter.payload()

            if 'LogicalOperator' in filter_payload:
                filter_part_left = self.soap_client.factory.create('SimpleFilterPart')
                for prop in filter_part_left:
                    if prop[0] in filter_payload['LeftOperand']:
                        filter_part_left[prop[0]] = filter_payload['LeftOperand'][prop[0]]

                filter_part_right = self.soap_client.factory.create('SimpleFilterPart')
                for prop in filter_part_right:
                    if prop[0] in filter_payload['RightOperand']:
                        filter_part_right[prop[0]] = filter_payload['RightOperand'][prop[0]]

                request_filter = self.soap_client.factory.create('ComplexFilterPart')
                request_filter.LeftOperand = filter_part_left
                request_filter.RightOperand = filter_part_right
                request_filter.LogicalOperator = filter_payload['LogicalOperator']
                for additional_operand in filter_payload.get('AdditionalOperands', []):
                    filter_part = self.soap_client.factory.create('SimpleFilterPart')
                    for k, v in list(additional_operand.items()):
                        filter_part[k] = v
                    request_filter.AdditionalOperands.Operand.append(filter_part)

                request.Filter = request_filter
            else:
                request_filter = self.soap_client.factory.create('SimpleFilterPart')
                for prop in request_filter:
                    if prop[0] in filter_payload:
                        request_filter[prop[0]] = filter_payload[prop[0]]
                request.Filter = request_filter

        if options is not None:
            for key, value in options.items():
                if isinstance(value, dict):
                    for k, v in value.items():
                        request.Options[key][k] = v
                else:
                    request.Options[key] = value

        return Response.make_from_service_response(self.soap_client.service.Retrieve(request))

    def parse_props_dict_into_ws_object(self, obj_type: str, props_dict: dict):
        """
        Build request payload for web service
        :param obj_type:    object type described at wsdl
        :param props_dict:  target object properties
        :return: web service object
        """
        ws_object = self.soap_client.factory.create(obj_type)
        for k, v in props_dict.items():
            if k in ws_object:
                ws_object[k] = v
            else:
                raise ValueError('{} is not a property of {}'.format(k, obj_type))

        return ws_object

    def parse_props_into_ws_object(self, obj_type, props):
        """
        Build request payload for web service
        :param obj_type:    object type described at wsdl
        :param props:  dict with target object property description or list of dict
        :return: web service object
        """
        if isinstance(props, dict):
            ws_object = self.parse_props_dict_into_ws_object(obj_type, props)
        elif isinstance(props, list):
            ws_object = [self.parse_props_dict_into_ws_object(obj_type, p) for p in props]
        else:
            message = 'Can not post properties to {} without a dict or list of properties'.format(obj_type)
            raise TypeError(message)

        return ws_object

    def soap_post(self, obj_type: str, props) -> Response:
        """
        Create request
        :param obj_type: object type described
        :param props:   dict|list   target object field in ws format
        :return: ws response
        """
        self.authenticator.refresh()
        payload = self.parse_props_into_ws_object(obj_type, props)

        return Response.make_from_service_response(self.soap_client.service.Create(None, payload))

    def soap_patch(self, obj_type: str, props) -> Response:
        """
        Update request
        :param obj_type: object type described
        :param props:   dict|list   target object field in ws format
        :return: ws response
        """
        self.authenticator.refresh()
        payload = self.parse_props_into_ws_object(obj_type, props)

        return Response.make_from_service_response(self.soap_client.service.Update(None, payload))

    def soap_delete(self, obj_type, props) -> Response:
        """
        Delete object
        :param obj_type: object type described
        :param props:   dict|list   target object field in ws format
        :return: ws response
        """
        self.authenticator.refresh()
        payload = self.parse_props_into_ws_object(obj_type, props)

        return Response.make_from_service_response(self.soap_client.service.Delete(None, payload))

    def soap_get_more_results(self, request_id: str) -> Response:
        """
        Retrieve more results
        :param request_id: Id of request marked as has more results
        :return: ws response
        """
        self.authenticator.refresh()
        request = self.soap_client.factory.create('RetrieveRequest')
        request.ContinueRequest = request_id

        return Response.make_from_service_response(self.soap_client.service.Retrieve(request))


class ClientFactory:
    """Produce Sales Force client"""

    def __init__(self):
        self._params = {}
        self._resource_bindings = {}
        self.soap_factory = None

    def bind_resource(self, handler: 'ResourceHandler') -> 'ClientFactory':
        """
        Bind resource handler
        :param handler: resource handler
        :return: self
        """
        self._resource_bindings[handler.get_resource_name()] = handler

        return self

    def bind_resources(self, handlers: List['ResourceHandler']) -> 'ClientFactory':
        for h in handlers:
            self.bind_resource(h)

    def set_params(self, params: dict, override=False) -> 'ClientFactory':
        """

        :param params:
        :param override: indicates about need override all previous params by given
        :return:
        """
        if not isinstance(params, dict):
            raise ValueError('params must be a dictionary')

        if override:
            self._params = params
        else:
            self._params.update(params)

        return self

    def make_authentificator(self) -> Authenticator:
        """Build Authentificator instance"""
        check_required_keys(self._params, ['client_id', 'client_secret'])
        authenticator = Authenticator(self._params.get('client_id'), self._params.get('client_secret'))

        if self._params.get('endpoint') not in (None, ''):
            authenticator.endpoint = self._params.get('endpoint')

        if self._params.get('appsignature') not in (None, ''):
            authenticator.appsignature = self._params.get('appsignature')

        if self._params.get('user_agent') not in (None, ''):
            authenticator.user_agent = self._params.get('user_agent')

        if any_keys_not_none(self._params, ['auth_token, auth_token_expiration, auth_legacy_token']):
            raise ConfigureError(
                'auth_token, auth_token_expiration, auth_legacy_token must be presented together and have no empty value')

        if all_keys_not_none(self._params, ['auth_token, auth_token_expiration, auth_legacy_token']):
            authenticator.auth_token = self._params['auth_token']
            authenticator.auth_token_expiration = self._params['auth_token_expiration']
            authenticator.auth_legacy_token = self._params['auth_legacy_token']
            if self._params['auth_refresh_token'] is not None:
                authenticator.auth_refresh_token = self._params['auth_refresh_token']

        authenticator.refresh()

        return authenticator

    def make_soap_factory(self):
        """Build soap client factory"""
        if self.soap_factory is None:
            check_required_keys(self._params, ['wsdl_local_path'])
            factory = SoapClientFactory(local_path=self._params.get('wsdl_local_path'))
            if any_keys_not_none(self._params, ['wsdl_url']):
                factory.url = self._params.get('wsdl_url')

            if any_keys_not_none(self._params, ['debug']):
                factory.debug = True if self._params.get('debug') in ('1', 'true', 'True', True) else False

            factory.init()
            self.soap_factory = factory

        return self.soap_factory

    def make(self) -> Client:
        """
        Build Sales Force Client
        :return: Client
        """
        client = Client()

        client.resource_handlers_map = self._resource_bindings
        client.authenticator = self.make_authentificator()
        client.soap_client_factory = self.make_soap_factory()

        client.refresh()

        return client

    def __repr__(self):
        txt = '<[{obj_class}][params:{params}][bindings:{bindings}]>'
        handlers_repr = []
        for k, v in self._resource_bindings.items():
            handlers_repr.append('{}->{}'.format(k, v.__name__))
        return txt.format(obj_class=self.__class__.__name__, params=self._params, bindings=",".join(handlers_repr))


class Attributable:

    def __init__(self, data: Mapping[str, Any]):
        self.raw_data = data
        self.data: Dict[str, Any] = {k: v for k, v in data}

    def __getattr__(self, item: str) -> Any:
        if item in self.data:
            return self.data[item]

        raise AttributeError("No such attribute: " + item)

    def __repr__(self):
        return "{}<{}>".format(self.__class__.__name__, self.data)


class EntityProperty(Attributable):
    pass


class Entity:
    """Present single object data"""

    TYPE: str = 'DefaultEntity'

    def __init__(self, data):
        self.raw_data = data

        self.data: Dict[str, Any] = {}
        self.properties: Dict[str, EntityProperty] = None

        for k, v in data:
            if k == 'Properties':
                props = {}
                for p in v[0]:
                    prop = EntityProperty(p)
                    props[prop.Name] = prop

                self.properties = props
                continue

            self.data[k] = v

    def has_properties(self) -> bool:
        """Check entity has any properties"""
        return self.properties is not None

    def get_type(self) -> str:
        """
        Get entity type, expected according to wsdl definition.
        Can be different if no way to determine it from response data
        """
        attr = getattr(self, 'Type')
        if attr is None:
            return self.TYPE

        return attr

    def get_property(self, name: str) -> EntityProperty:
        """
        Get property if exists else throw MissingProperty exception
        :param name:
        :return:
        """

        if not self.has_properties():
            raise ResourceMissingPropertyException("Entity[{}] has no any properties".format(self.get_type()))

        if name not in self.properties:
            raise ResourceMissingPropertyException('Missing property [{}]'.format(name))

        return self.properties[name]

    def get_property_value(self, name: str) -> Any:
        """
        Get property value if exists else throw MissingProperty exception
        :param name:
        :return:
        """

        return self.get_property(name).Value

    def get_properties(self) -> List[EntityProperty]:
        if not self.has_properties():
            raise ResourceMissingPropertyException('Entity[{}] has no any properties'.format(self.get_type()))

        return list(self.properties.values())

    def __iter__(self) -> Iterable:
        return iter(self.data)

    def __getattr__(self, item) -> Any:
        if item == 'Properties':
            if not self.has_properties():
                raise AttributeError('No such attribute [{}]'.format(item))
            return self.get_properties()

        if item not in self.data:
            raise AttributeError('No such attribute [{}]'.format(item))

        return self.data[item]

    def __repr__(self) -> str:
        return "{}[data:{},properties:{}]".format(self.__class__.__name__, self.data, self.properties)


class ObjectDefinitionProperty(Attributable):
    """Describe property for object definition"""

    @classmethod
    def make_from_seq(cls, seq: Iterable[Mapping[str, Any]]) -> 'List[ObjectDefinitionProperty]':
        return [cls(p) for p in seq]


class ObjectDefinition:
    def __init__(self, object_type: str, properties: Iterable[Any]):
        self.obj_type = object_type
        self.raw_props = properties
        self.props = {p.Name: p for p in ObjectDefinitionProperty.make_from_seq(properties)}

    def properties(self) -> MutableMapping[str, ObjectDefinitionProperty]:
        return self.props

    def get_property(self, name: str) -> ObjectDefinitionProperty:
        if name not in self.props:
            raise ResourceMissingPropertyException("Missing property: " + name)

        return self.props[name]

    def retrievable_properties(self) -> List[ObjectDefinitionProperty]:
        """Properties retrievable from API"""
        target = []
        for p in self.properties().values():
            # skip unexpected IsPlatformObject property cause it's not declared at wsdl schema and
            # it's impossible to request this property
            if p.Name == 'IsPlatformObject' or not p.IsRetrievable:
                continue
            target.append(p)

        return target

    def retrievable_property_names(self) -> List[str]:
        return [p.Name for p in self.retrievable_properties()]

    def __repr__(self) -> str:
        return "{}[object_type:{},properties:{}]".format(self.__class__.__name__, self.obj_type, self.props)


class ResourceBase:
    """Describe API resource interface. Used for represent API response"""

    entity_factory: Callable = None

    def __init__(self):
        self.handler: 'ResourceHandler' = None
        self.response: Response = None

    @classmethod
    def get_entity_factory(cls) -> Callable:
        """Return factory for building dataset entities"""
        if cls.entity_factory is None:
            return Entity

        return cls.entity_factory

    def __iter__(self):

        def it(resource: 'ResourceBase'):
            index = 0
            stop = False
            entities = resource.entities
            while not stop:
                if index >= len(entities):
                    if resource.has_more_results:
                        resource = resource.get_more_results()
                        entities = resource.entities
                        index = 0
                    else:
                        stop = True

                    continue

                yield entities[index]

                index += 1

        return it(self)

    @classmethod
    def make_from_response(cls, handler: 'ResourceHandler', response: Response) -> 'ResourceBase':
        """
        Build resource from soap-service response
        :param handler:     resource handler
        :param response:    service response
        :return:
        """
        resource = cls()
        resource.handler = handler
        resource.response = response

        return resource

    @property
    def entities(self) -> List[Entity]:
        """Dataset entities"""
        f = self.get_entity_factory()

        return [f(r) for r in self.response.results]

    def __repr__(self):
        return "Resource<handler[{}],response[{}]>".format(self.handler.get_resource_name(), self.response)

    @property
    def entities_count(self) -> int:
        """Dataset entities count"""
        return len(self.response.results)

    @property
    def is_empty(self) -> bool:
        """Contain empty dataset"""
        return self.response.is_empty

    @property
    def has_more_results(self) -> bool:
        """Is available next portion of data"""
        return bool(self.response.more_results)

    def get_more_results(self) -> 'ResourceBase':
        """Next portion of data if available else raise error"""
        if not self.has_more_results:
            raise NoMoreDataAvailable('No more data available for request[{}]'.format(self.response.request_id))

        return self.handler.more_results(self.response.request_id)

    @property
    def is_valid(self):
        """Resource contain data of valid service response"""
        return self.response.is_valid


class ResourceHandler:
    """
    Describe API resource handler interface. Used for interact with API"""

    """Type of resource determined at wsdl"""
    resource_type: str = None
    """Class for represent soap-service response"""
    resource_base = ResourceBase
    """Human readable name for resource"""
    resource_name: str = None

    def __init__(self, client):
        self.client: Client = client

    @classmethod
    def get_resource_type(cls) -> str:
        """Resource type as described at wsdl"""
        if cls.resource_type is None:
            raise NotImplementedError("Need setup resource type")

        return cls.resource_type

    def make_resource(self, response: Response) -> ResourceBase:
        """Build wrapper for resource from soap-service response"""
        return self.resource_base.make_from_response(self, response)

    @classmethod
    def get_resource_name(cls) -> str:
        """Custom name for resource type. In some case can be more expressive."""
        if cls.resource_name is not None:
            return cls.resource_name

        return cls.get_resource_type()

    def describe(self) -> ObjectDefinition:
        """Object definition"""
        resp = self.client.soap_describe_object(self.get_resource_type())

        if not resp.is_valid or resp.is_empty:
            raise ResourceHandlerException('Invalid response or response dataset is empty[{}]'.format(resp))

        obj_type = resp.results[0]['ObjectType']
        props = resp.results[0]['Properties']

        return ObjectDefinition(obj_type, props)

    def more_results(self, request_id: str) -> ResourceBase:
        """
        Get next portion of data
        :param request_id: Previous request marked as has more available results
        :return: next results portion wrapped into ResourceBase
        """
        resp = self.client.soap_get_more_results(request_id)

        return self.make_resource(resp)
