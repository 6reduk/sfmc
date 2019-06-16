import os
import unittest
import json

from sfmc import Client, client_factory

INCLUDE_LONG_TESTS = bool(os.getenv('LONG_TESTS', False))
ALLOW_BASED_ON_INTERNAL_CREDS_TESTS = bool(os.getenv('ALLOW_INTERNAL', False))


class TestCase(unittest.TestCase):
    """
    Base class for any sfmc unit tests
    """

    mc_config: dict = None

    @classmethod
    def get_mc_credentials(cls):
        if cls.mc_config is None:
            path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'config.json'))
            with open(path, 'r') as f:
                cls.mc_config = json.load(f)

        return cls.mc_config

    @classmethod
    def get_mc_client(cls) -> Client:
        creds = cls.get_mc_credentials()
        client_factory.set_params(creds)

        return client_factory.make()
