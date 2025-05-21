"""
UnitTest transformation_step file
"""
import unittest
from unittest import mock

from ant_py import Package
from steps.transformation_step import TransformationStep

class TestTransformationStep(unittest.TestCase):
    """
    Clase para probar los métodos del Step
    """

    # ---------- Inicializador ---------- #
    def initialize(self):
        self.test_validations = TransformationStep(name='validations')

        self.params_ok = [
            [{'SellingLocationId': '0035','ShipFromLocationId': '0020','UpdatedTimestamp': '20201106','ItemId': '1136410','Quantity': 10,'OrdernumberId': '010417200035351007909','MinFulfillmentStatusId': '2000','IsOnHold': True}]
        ]

        self.params_ok_header = [
            {'id': '1604676410851', 'messages': {'messagesIn': 0,'messagesFilter': 0,'messagesOut': 0,'messagesError': 0, 'messagesBlocks': 0}},
        ]

        self.params_error = [
            ["error"]
        ]

        self.params_error_header = [
            {'id': '1604676410851', 'messages': {'messagesIn': 0,'messagesFilter': 0,'messagesOut': 0,'messagesError': 0, 'messagesBlocks': 0}}
        ]

        self.data = {'SellingLocationId': '0035','ShipFromLocationId': '0020','UpdatedTimestamp': '20201106','ItemId': '1136410','Quantity': 10,'OrdernumberId': '010417200035351007909','MinFulfillmentStatusId': '2000','IsOnHold': True}

        self.data_convert = [
            '0035',
            '2020-11-06T15:26:45.562',
            10,
            True,
            '',
            12.5,
            None
        ]

    def ok_package_initialize(self, params, paramsheader):
        self.ok_package = Package()
        self.ok_package.message_in.body = params
        self.ok_package.message_in.header = paramsheader
        self.ok_package.status = Package.OK

    def error_package_initialize(self, params, paramsheader):
        self.error_package = Package()
        self.error_package.message_in.body = params
        self.error_package.message_in.header = paramsheader
        self.error_package.status = Package.OK

    # ---------- Unit Test ---------- #
    def test_call_ok(self):
        self.initialize()
        i = len(self.params_ok)
        x = 0
        while x < i:
            self.ok_package_initialize(self.params_ok[x], self.params_ok_header[x])
            package = self.test_validations.__call__(self.ok_package)

            self.assertEqual(
                package.message_in.header['messages']['messagesOut'],
                1
            )

            self.assertEqual(
                package.message_in.header['messages']['messagesBlocks'],
                1
            )

            self.assertEqual(
                type(package.message_in.body),
                list
            )

            self.assertEqual(
                type(package.message_in.header),
                dict
            )

            x += 1

    def test_call_error(self):
        self.initialize()
        i = len(self.params_error)
        x = 0
        while x < i:
            self.error_package_initialize(self.params_error[x], self.params_error_header[x])
            package = self.test_validations.__call__(self.error_package)

            self.assertEqual(
                package.status,
                package.ERROR
                )

            self.assertTrue(
                package.desc_status !=
                ''
            )
            self.assertEqual(
                package.message_in.header['messages']['messagesOut'],
                0
            )

            self.assertEqual(
                package.message_in.header['messages']['messagesError'],
                1
            )

            x += 1

    def test_set_structure(self):
        self.initialize()
        data = self.test_validations.set_structure(self.data)

        self.assertEqual(
            len(data),
            1273
        )

        self.assertEqual(
            type(data),
            str
        )

    def test_convert_str(self):
        self.initialize()
        i = len(self.data_convert)
        x = 0
        while x < i:
            data_convert = self.test_validations.convert_str(self.data_convert[x])
            self.assertEqual(
                type(data_convert),
                str
            )
            x += 1
