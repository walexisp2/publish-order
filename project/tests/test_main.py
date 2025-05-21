"""
    UnitTest de la clase main.py
"""
import sys
import json
import unittest
from unittest import mock

sys.modules['ant_ibmmq'] = mock.MagicMock()
sys.modules['ant_rabbitmq'] = mock.MagicMock()

from get_environment import GetEnvironment

from tests.test_get_environment import TestGetEnvironment
from tests.test_transformation_step import TestTransformationStep
from tests.test_trace_step import TestTraceStep
from tests.test_validations_step import TestValidationStep


class TestMain(unittest.TestCase):
    """
        Clase para probar los métodos del Main
    """

    def test_main(self):
        """Método que prueba la clase main"""
        with open("config/config.json") as json_file:
            CONFIG = json.load(json_file)

        with mock.patch.object(
            GetEnvironment, 'get_mapping', return_value=CONFIG
        ):
            import main
            instances = main.get_instances(CONFIG)
            process = main.init_process(instances, CONFIG)

            self.assertIsNotNone(CONFIG)
            self.assertIsNotNone(instances.get("source_rabbitmq"))
            self.assertIsNotNone(instances.get("trace_step"))
            self.assertIsNotNone(instances.get("validation_step"))
            self.assertIsNotNone(instances.get("transformation_step"))
            self.assertIsNotNone(instances.get("target_ibmmq"))
            self.assertIsNotNone(instances.get("elk"))
            self.assertIsNotNone(process)

            self.assertEqual(
                type(CONFIG),
                dict
            )

            self.assertEqual(
                len(CONFIG),
                6
            )

            self.assertTrue(
                CONFIG['SOURCE_RABBIT']['password'] != '' or
                CONFIG['SOURCE_RABBIT']['password'] != None
            )

            self.assertTrue(
                CONFIG['TARGET_IBMMQ']['password'] != '' or
                CONFIG['TARGET_IBMMQ']['password'] != None
            )

            self.assertTrue(
                CONFIG['RABBITMQ_TRACE']['password'] != '' or
                CONFIG['RABBITMQ_TRACE']['password'] != None
            )

if __name__ == '__main__':
    unittest.main()
