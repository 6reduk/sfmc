class ConfigureError(Exception):
    """Package configuration exception"""
    pass


class AuthenticationError(Exception):
    """Auth error"""
    pass


class APIRequestError(Exception):
    """Base error for all api requests"""
    pass


class SOAPRequestError(APIRequestError):
    """Base error for soap requests"""
    pass


class ResourceHandlerException(Exception):
    """Base error for resource handler operations"""
    pass


class ResourceMissingPropertyException(ResourceHandlerException):
    pass
