import os
import time
import datetime
import json
import logging
import requests
from suds.client import Client as SoapClient
from suds.wsse import Security, UsernameToken
from suds.sax.element import Element
from .exceptions import ConfigureError, AuthenticationError, APIRequestError, SOAPRequestError
from .resources.filter import SearchFilter


class ClientFactory:
    """Produce Sales Force client"""
    def __init__(self):
        self._params = {}
        self._resource_bindings = {}

    def bind_resource(self, handler):
        """Bind resource to handler"""
        self._resource_bindings[handler.get_resource_name()] = handler

        return self

    def set_params(self, params, override=False):
        if not isinstance(params, dict):
            raise ValueError('params must be a dictionary')

        if override:
            self._params = params
        else:
            self._params.update(params)

    def make(self):
        # For all available client options see Client constructor method
        client = Client()

        client.resource_handlers_map = self._resource_bindings

        if self._params.get('client_id') not in (None, ''):
            client.client_id = self._params.get('client_id')
        else:
            raise ConfigureError('client_id is required and must has not empty value.')

        if self._params.get('client_secret') not in (None, ''):
            client.client_secret = self._params.get('client_secret')
        else:
            raise ConfigureError('client_secret is required and must has not empty value.')

        if self._params.get('endpoint') not in (None, ''):
            client.endpoint = self._params.get('endpoint')

        if self._params.get('appsignature') not in (None, ''):
            client.appsignature = self._params.get('appsignature')

        auth_token = self._params.get('auth_token')
        auth_token_expiration = self._params.get('auth_token_expiration')
        auth_legacy_token = self._params.get('auth_legacy_token')
        auth_refresh_token = self._params.get('auth_refresh_token')

        if all(map(lambda x: x is not None, [auth_token, auth_token_expiration, auth_legacy_token])):
            client.auth_token = auth_token
            client.auth_token_expiration = auth_token_expiration
            client.auth_legacy_token = auth_legacy_token
            if auth_refresh_token is not None:
                client.auth_refresh_token = auth_refresh_token
        elif any(map(lambda x: x is not None, [auth_token, auth_token_expiration, auth_legacy_token])):
            raise ConfigureError(
                'auth_token, auth_token_expiration, auth_legacy_token must be presented together and not to have empty value')

        if self._params.get('wsdl_local_path') not in (None, ''):
            client.wsdl_local_path = self._params.get('wsdl_local_path')
        else:
            raise ConfigureError('wsdl_local_path is required and must has not empty value')

        if self._params.get('wsdl_url') not in (None, ''):
            client.wsdl_url = self._params.get('wsdl_url')

        if self._params.get('user_agent') not in (None, ''):
            client.user_agent = self._params.get('user_agent')

        if self._params.get('debug') not in (None, ''):
            debug_flag = True if self._params.get('debug') in ('1', 'true', 'True', True) else False
            client.set_debug(debug_flag)

        client.init()

        return client

    def __repr__(self):
        txt = '<[{obj_class}][params:{params}][bindings:{bindings}]>'
        handlers_repr = []
        for k, v in self._resource_bindings.items():
            handlers_repr.append('{}->{}'.format(k, v.__name__))
        return txt.format(obj_class=self.__class__.__name__, params=self._params, bindings=",".join(handlers_repr))


class Client:
    """Sales Force client.
    Call resource handlers dynamically based on their name:
    client.some_resource.action(args, kwargs)
    """

    def __init__(self):
        self.wsdl_url = 'https://webservice.exacttarget.com/etframework.wsdl'
        self.auth_url = 'https://auth.exacttargetapis.com/v1/requestToken?legacy=1'
        self.user_agent = 'sfmc'
        self.wsdl_local_path = None
        self.wsdl_local_file_expire_timeout = 60 * 60 * 24  # 1 day in seconds
        self.endpoint = None
        self.resource_handlers_map = {}
        self.resource_handlers = {}
        self.auth_token_expiration = None
        self.auth_legacy_token = None
        self.auth_refresh_token = None
        self.soap_client = None
        self.client_id = None
        self.client_secret = None
        self.appsignature = None
        self.auth_token = None
        self._wsdl_local_file_url = None  # used only for build soap client
        self._debug = False

    def _download_wsdl(self, wsdl_url, local_path):
        with open(local_path, 'w') as of:
            r = requests.get(wsdl_url)
            of.write(r.text)

    def _local_wsdl_is_expired(self, local_path):
        ts = time.mktime(time.gmtime(os.path.getmtime(local_path)))
        d = time.mktime(datetime.datetime.now().timetuple())

        return ts + self.wsdl_local_file_expire_timeout < d

    def fetch_wsdl(self):
        if not os.path.exists(self.wsdl_local_path) \
                or os.path.getsize(self.wsdl_local_path) == 0 \
                or self._local_wsdl_is_expired(self.wsdl_local_path):
            self._download_wsdl(self.wsdl_url, self.wsdl_local_path)
        self._wsdl_local_file_url = 'file:///' + self.wsdl_local_path

    def _auth_token_expired(self):
        if self.auth_token is None:
            return True

        if self.auth_token_expiration is None:
            return True

        if self.auth_token_expiration < time.time() + 300:
            return True

        return False

    def refresh_token(self):
        if not self._auth_token_expired():
            return

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
        if 'refreshToken' in response_body:
            self.auth_refresh_token = response_body['refreshToken']

    def _detect_endpoint(self):
        url = 'https://www.exacttargetapis.com/platform/v1/endpoints/soap?access_token=' + self.auth_token
        headers = {'user-agent': self.user_agent}

        try:
            res = requests.get(url, headers)
            response_body = res.json()
            if 'url' in response_body:
                return str(response_body['url'])
        except Exception as e:
            raise APIRequestError('Unable to determine endpoints stack: ' + str(e))

    def build_soap_client(self):
        if self.endpoint is None:
            self.endpoint = self._detect_endpoint()

        self.soap_client = SoapClient(self._wsdl_local_file_url, faults=False, cachingpolicy=1)
        self.soap_client.set_options(location=self.endpoint)

        security = Security()
        token = UsernameToken('*', '*')
        security.tokens.append(token)
        self.soap_client.set_options(wsse=security)

        element_oauth = Element('oAuth', ns=('etns', 'http://exacttarget.com'))
        element_oauth_token = Element('oAuthToken').setText(self.auth_legacy_token)
        element_oauth.append(element_oauth_token)
        self.soap_client.set_options(soapheaders=[element_oauth])

        if self._debug:
            logging.basicConfig(level=logging.INFO)
            logging.getLogger('suds.client').setLevel(logging.DEBUG)
            logging.getLogger('suds.transport').setLevel(logging.DEBUG)
            logging.getLogger('suds.xsd.schema').setLevel(logging.DEBUG)
            logging.getLogger('suds.wsdl').setLevel(logging.DEBUG)
        else:
            logging.getLogger('suds').setLevel(logging.INFO)

    def init(self):
        self.fetch_wsdl()
        self.refresh_token()
        self.build_soap_client()

    def __getattr__(self, item):
        if item not in self.resource_handlers_map:
            raise LookupError('Missing handler for resource ' + item)

        if item not in self.resource_handlers:
            self.resource_handlers[item] = self.resource_handlers_map[item](self)

        return self.resource_handlers[item]

    def set_debug(self, debug):
        self._debug = debug

    def soap_describe_object(self, obj_type):
        self.refresh_token()

        request = self.soap_client.factory.create('ArrayOfObjectDefinitionRequest')

        obj_definition = {'ObjectType': obj_type}
        request.ObjectDefinitionRequest = [obj_definition]

        response = self.soap_client.service.Describe(request)

        if response is None:
            raise SOAPRequestError('Empty response for describe request for {} object type'.format(obj_type))

        return response

    def soap_get(self, obj_type, search_filter=None, props=None, options=None):
        self.refresh_token()

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

        return self.soap_client.service.Retrieve(request)

    def parse_props_dict_into_ws_object(self, obj_type, props_dict):
        ws_object = self.soap_client.factory.create(obj_type)
        for k, v in props_dict.items():
            if k in ws_object:
                ws_object[k] = v
            else:
                raise ValueError('{} is not a property of {}'.format(k, obj_type))

        return ws_object

    def parse_props_into_ws_object(self, obj_type, props):
        if isinstance(props, dict):
            ws_object = self.parse_props_dict_into_ws_object(obj_type, props)
        elif isinstance(props, list):
            ws_object = [self.parse_props_dict_into_ws_object(obj_type, p) for p in props]
        else:
            message = 'Can not post properties to {} without a dict or list of properties'.format(obj_type)
            raise TypeError(message)

        return ws_object

    def soap_post(self, obj_type, props):
        payload = self.parse_props_into_ws_object(obj_type, props)

        return self.soap_client.service.Create(None, payload)

    def soap_patch(self, obj_type, props):
        payload = self.parse_props_into_ws_object(obj_type, props)

        return self.soap_client.service.Update(None, payload)

    def soap_delete(self, obj_type, props):
        payload = self.parse_props_into_ws_object(obj_type, props)

        return self.soap_client.service.Delete(None, payload)
