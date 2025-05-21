"""
    UnitTest de la clase get_environment.py
"""
import os
import unittest
from unittest import mock

from get_environment import GetEnvironment


class TestGetEnvironment(unittest.TestCase):
    """
        Clase para probar los métodos del get_environment
    """
    @mock.patch.dict(os.environ, {"SOURCE_RABBIT": '{"TEST": true}'})
    @mock.patch.dict(os.environ, {"TRACEABILITY": '{"TEST": true}'})
    @mock.patch.dict(os.environ, {"RABBITMQ_TRACE": '{"TEST": true}'})
    @mock.patch.dict(os.environ, {"GENERAL": '{"TEST": true}'})
    @mock.patch.dict(os.environ, {"TARGET_IBMMQ": '{"TEST": true}'})
    @mock.patch.dict(os.environ, {"FILTERS": '{"TEST": true}'})
    def test_attack(self):
        """
            Método para probar la función get_mapping
        """
        self.assertIsNotNone(
            GetEnvironment.get_mapping()
        )
        self.assertEqual(
            GetEnvironment.get_mapping()['SOURCE_RABBIT'],
            {'TEST': True, 'password': None}
        )
        self.assertEqual(
            GetEnvironment.get_mapping()['GENERAL'],
            {'TEST': True}
        )
        self.assertEqual(
            GetEnvironment.get_mapping()['RABBITMQ_TRACE'],
            {'TEST': True, 'password': None}
        )
        self.assertEqual(
            GetEnvironment.get_mapping()['TRACEABILITY'],
            {'TEST': True}
        )
        self.assertEqual(
            GetEnvironment.get_mapping()['TARGET_IBMMQ'],
            {'TEST': True, 'password': None}
        )
        self.assertEqual(
            GetEnvironment.get_mapping()['FILTERS'],
            {'TEST': True}
        )
