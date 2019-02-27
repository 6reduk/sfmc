"""Describe all api resources and resource handlers interface and concrete resource/handlers resources"""
from ..util import suds_results_to_simple_types


class ResourceBase:
    """Describe API resource interface. Used for represent API response"""

    def __init__(self, results, code, status, message, more_results, request_id):
        self.results = results
        self.code = code
        self.status = status
        self.message = message
        self.more_results = more_results
        self.request_id = request_id

    @classmethod
    def make_from_response(cls, response=None, is_rest=False):
        results = []
        code = None
        status = False
        message = None
        more_results = False
        request_id = None

        if response is None:
            return cls(results, code, status, message, more_results, request_id)

        if is_rest:
            code = response.status_code
            status = True if code == 200 else False
            results = response.json()
        else:  # soap call
            code = response[0]  # suds puts the code in tuple position 0
            body = response[1]  # and the result in tuple position 1

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

        return cls(results, code, status, message, more_results, request_id)

    def __repr__(self):
        msg = "Resource<request_id[{}],results[{}],code[{}],status[{}],message[{}],more_results[{}]>"

        return msg.format(self.request_id, suds_results_to_simple_types(self.results), self.code, self.status, self.message, self.more_results)

    def retrievable_properties(self):
        return [prop for prop in self.properties() if prop.IsRetrievable and prop.Name != 'IsPlatformObject']   #skip unexpected IsPlatformObject property. It's not declared at wsdl schema, seems like API Bug

    def is_single_object(self):
        return 'Properties' in self.results[0]

    def properties(self):
        try:
            return self.results[0].Properties
        except IndexError:
            return []

    def is_empty(self):
        return len(self.results) == 0


class ResourceHandler:
    """
    Describe API resource handler interface. Used for interact with API"""
    resource_type = None
    resource_base = None

    def __init__(self, client):
        self.client = client

    @classmethod
    def get_resource_type(cls):
        if cls.resource_type is None:
            raise NotImplementedError("Need setup resource type")

        return cls.resource_type

    @classmethod
    def make_resource_from_response(cls, response):
        return cls.resource_base.make_from_response(response)

    @classmethod
    def get_resource_name(cls):
        return cls.get_resource_type()

    def describe(self):
        response = self.client.soap_describe_object(self.get_resource_type())

        return ResourceBase.make_from_response(response)

