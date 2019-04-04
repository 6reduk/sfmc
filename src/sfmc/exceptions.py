class BasePackageException(Exception):
    """Base exception for all package exceptions"""
    pass


class ConfigureError(BasePackageException):
    """Package configuration exception"""
    pass


class AuthenticationError(BasePackageException):
    """Auth error"""
    pass


class APIRequestError(BasePackageException):
    """Base error for all api requests"""
    pass


class SOAPRequestError(APIRequestError):
    """Base error for soap requests"""
    pass


class ResourceHandlerException(BasePackageException):
    """Base error for resource handler operations"""
    pass


class ResourceMissingPropertyException(ResourceHandlerException):
    """Missing object property"""
    pass


class NoMoreDataAvailable(BasePackageException):
    """Dataset is ended and no more data available"""
    pass
