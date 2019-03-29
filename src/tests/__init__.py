import sys
import os
import unittest
import json


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
