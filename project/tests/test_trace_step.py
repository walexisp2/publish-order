"""
UnitTest trace_step file
"""
import unittest
from unittest import mock
from json import loads

from ant_py import Package

from steps.trace_step import TraceStep

class TestTraceStep(unittest.TestCase):
    """
    Clase para probar los métodos del Step
    """
    # ---------- Inicializador ---------- #
    def initialize(self):
        self.trace_step = TraceStep(name='test_trace_step')

        self.ok_package_initialize()
        self.error_package_initialize()

    def ok_package_initialize(self):
        self.ok_package = Package()
        self.ok_message = [
            ['{"name":"publish.order","eventId":"46c11c3d-629d-4a42-8572-b44963391611","data":{"header":{"transactionId":"9762e072-1772-46e1-b83f-d607c0216eff","applicationId":"oms-publish-order","hostname":"oms-publish-order","user":"MAO","transactionDate":1605645824891,"esb":null,"errors":[{"code":"0","type":"Ejecución exitosa","description":null}]},"data":{"publishOrderDto":{"orderId":"010417200035351009707","alternateOrderId":null,"createdBy":"jcadavida@Grupo-Exito.com","orderTypeId":"mPos Order","createdTimestamp":"2020-11-17T20:43:27.61","orderCapturedDttm":"2020-11-17T20:43:27.61","orderConfirmedDttm":null,"currencyCode":"COP","orderSubTotal":5858649,"orderTotal":5858649,"orgId":"GEOMNICANAL","sellingLocationId":"0035","sellingChannelId":"Store","customerId":"2_93101829","customerFirstName":"PRUEBA","customerLastName":"SOBREVENTA","customerTypeId":null,"customerEmail":"SOBREVENTA@GMAIL.COM","customerPhone":"3007700019","doNotReleaseBefore":null,"docTypeId":"CustomerOrder","secondCustomerCellphoneNumber":null,"scheduleDeliveryDttm":null,"isCancelled":false,"isConfirmed":false,"isOnHold":true,"orderLineCount":"1","totalCharges":null,"totalDiscounts":null,"puntos":null,"minutos":null,"orderSalesAssociateList":[{"associateId":"jcadavida"}],"orderPaymentList":null,"orderNoteList":null,"releaseList":null,"orderHoldList":null,"orderTaxDetailList":null,"orderLineList":[{"alternateOrderLineId":null,"minFulfillmentStatusId":"2000","carrierCode":null,"createdTimestamp":"2020-11-17T20:43:27.613","deliveryMethodId":"ShipToAddress","giftCardValue":null,"isCancelled":false,"isGift":false,"isGiftCard":false,"orderId":"010417200035351009707","orderLineId":"1","orderLineSubTotal":5858649,"orderLineTotal":5858649,"orgId":"GEOMNICANAL","isReturn":false,"itemId":"1444868","updatedTimestamp":"2020-11-17T20:43:29.08","maxFulfillmentStatusId":"2000","quantity":1,"cancelQuantity":null,"uom":"Units","unitPrice":5858649,"parentOrderId":null,"parentOrderLineId":null,"promisedDeliveryDttm":null,"promisedShipDttm":null,"sellingLocationId":"0035","shipFromAddressId":null,"shipToLocationId":null,"shippingMethodId":"SHIPMT1_CC","totalDiscounts":null,"totalTaxes":null,"estimatedWeight":null,"isWeightVariable":null,"estimatedWeightUOM":null,"orderLinePromisingInfo":null,"orderLineShipToAddress":{"isAddressVerified":false,"address1":"CALLE50a 35 20","address2":"APTO503","billingAddress":"TORRE 2","city":"ENVIGADO","country":"CO","county":"EL DORADO","email":"SOBREVENTA@GMAIL.COM","firstName":"PRUEBA","lastName":"SOBREVENTA","phone":"3007700019","state":"ANTIOQUIA","postalCode":"05266"},"orderLineChargeDetailList":null,"orderLineTaxDetailList":null,"orderLineVasInstructionsList":null,"orderLineNoteList":null,"orderLineAllocationList":[{"asnDetailId":null,"asnId":null,"shipViaId":"SHIPV1_CC","shipFromLocationId":"0020"}],"orderLineCancelHistory":null}],"orderChargeDetailList":null}}}}'],
            ['{"name":"publish.order","eventId":"c8dbdad6-d7fd-489a-a055-7a53649de4de","data":{"header":{"transactionId":"86edeccf-ab08-4bd1-a4ff-3c7186b05c3a","applicationId":"oms-publish-order","hostname":"oms-publish-order","user":"MAO","transactionDate":1605647490688,"esb":null,"errors":[{"code":"0","type":"Ejecución exitosa","description":null}]},"data":{"publishOrderDto":{"orderId":"010417200035351009707","alternateOrderId":null,"createdBy":"jcadavida@Grupo-Exito.com","orderTypeId":"mPos Order","createdTimestamp":"2020-11-17T20:43:27.61","orderCapturedDttm":"2020-11-17T20:43:27.61","orderConfirmedDttm":null,"currencyCode":"COP","orderSubTotal":0,"orderTotal":0,"orgId":"GEOMNICANAL","sellingLocationId":"0035","sellingChannelId":"Store","customerId":"2_93101829","customerFirstName":"PRUEBA","customerLastName":"SOBREVENTA","customerTypeId":null,"customerEmail":"SOBREVENTA@GMAIL.COM","customerPhone":"3007700019","doNotReleaseBefore":null,"docTypeId":"CustomerOrder","secondCustomerCellphoneNumber":null,"scheduleDeliveryDttm":null,"isCancelled":true,"isConfirmed":false,"isOnHold":true,"orderLineCount":"1","totalCharges":null,"totalDiscounts":null,"puntos":null,"minutos":null,"orderSalesAssociateList":[{"associateId":"jcadavida"}],"orderPaymentList":null,"orderNoteList":null,"releaseList":null,"orderHoldList":[{"createdTimestamp":"2020-11-17T20:44:04.729","externalCreatedBy":null,"externalCreatedDate":null,"holdTypeId":"Suspended","orgId":"GEOMNICANAL","statusId":"1000","updatedBy":"jcadavida@Grupo-Exito.com"}],"orderTaxDetailList":null,"orderLineList":[{"alternateOrderLineId":null,"minFulfillmentStatusId":"9000","carrierCode":null,"createdTimestamp":"2020-11-17T20:43:27.613","deliveryMethodId":"ShipToAddress","giftCardValue":null,"isCancelled":true,"isGift":false,"isGiftCard":false,"orderId":"010417200035351009707","orderLineId":"1","orderLineSubTotal":0,"orderLineTotal":0,"orgId":"GEOMNICANAL","isReturn":false,"itemId":"1444868","updatedTimestamp":"2020-11-17T21:11:25.94","maxFulfillmentStatusId":"9000","quantity":0,"cancelQuantity":null,"uom":"Units","unitPrice":5858649,"parentOrderId":null,"parentOrderLineId":null,"promisedDeliveryDttm":null,"promisedShipDttm":null,"sellingLocationId":"0035","shipFromAddressId":null,"shipToLocationId":null,"shippingMethodId":"SHIPMT1_CC","totalDiscounts":null,"totalTaxes":null,"estimatedWeight":null,"isWeightVariable":null,"estimatedWeightUOM":null,"orderLinePromisingInfo":null,"orderLineShipToAddress":{"isAddressVerified":false,"address1":"CALLE50a 35 20","address2":"APTO503","billingAddress":"TORRE 2","city":"ENVIGADO","country":"CO","county":"EL DORADO","email":"SOBREVENTA@GMAIL.COM","firstName":"PRUEBA","lastName":"SOBREVENTA","phone":"3007700019","state":"ANTIOQUIA","postalCode":"05266"},"orderLineChargeDetailList":null,"orderLineTaxDetailList":null,"orderLineVasInstructionsList":null,"orderLineNoteList":null,"orderLineAllocationList":null,"orderLineCancelHistory":[{"cancelQuantity":1}]}],"orderChargeDetailList":null}}}}'],
            ['{"data":{"header":{},"data":{"publishOrderDto":{}}}}'],
            ['{"data":{"header":{},"data":{}}}'],
            ['{"data":{}}'],
            ['{}']
        ]
        self.ok_message_header = [
            {"transactionId":"6f9dedcd-e76a-4d7a-9ee8-ffc271a2f9e5", "applicationId":"oms-publish-order", "hostname":"oms-publish-order", "user":"MAO"},
            {}
        ]

    def error_package_initialize(self):
        self.error_package = Package()
        self.error_message = [
            ['<ns2:root-element xmlns:ns2="http://www.grupoexito.com/upload7_sinco_out"><ns2:element><ns2:tipoMsg>SHIP</ns2:tipoMsg><ns2:ins>013</ns2:ins><ns2:uploadRecord>53551280</ns2:uploadRecord><ns2:transactionClass>INVEQTY</ns2:transactionClass><ns2:transactionObjec>OBO</ns2:transactionObjec><ns2:transactionAction>SHIP</ns2:transactionAction><ns2:transactionDate>2020-09-15T21:54:32.000-05:00</ns2:transactionDate><ns2:container>D14600503544</ns2:container><ns2:outermostContainer>D14600503544</ns2:outermostContainer><ns2:operatorId>ADDELGADOT</ns2:operatorId><ns2:originalOrderQty>1</ns2:originalOrderQty><ns2:orderQuantity>1</ns2:orderQuantity><ns2:part>1464526</ns2:part><ns2:old>N</ns2:old><ns2:tag>013</ns2:tag><ns2:holdCode/><ns2:oldHoldCode>Y</ns2:oldHoldCode><ns2:orderId>0035452936</ns2:orderId><ns2:orderType>S10</ns2:orderType><ns2:lineItemNumber>000001</ns2:lineItemNumber><ns2:carrier>000888888804</ns2:carrier><ns2:trailer>AAA000</ns2:trailer><ns2:probillNumber>0155690563</ns2:probillNumber><ns2:warehouse>013</ns2:warehouse><ns2:groupCode1/><ns2:groupCode2>013</ns2:groupCode2><ns2:groupCode3>552</ns2:groupCode3><ns2:groupCode4>10</ns2:groupCode4><ns2:groupCode5>0362</ns2:groupCode5><ns2:groupCode6>01460362999</ns2:groupCode6><ns2:totalPieces>1</ns2:totalPieces><ns2:freigthTerms>11</ns2:freigthTerms><ns2:shipToName>0362</ns2:shipToName><ns2:owner>EXITO</ns2:owner><ns2:seal/></ns2:element></ns2:root-element>'],
            ['{"data":""}'],
            ['{"data":[]}'],
            ['{"data":null}'],
            ['data'],
            ['null'],
            [None],
            []
        ]

    # ---------- Unit Test ---------- #
    def test__call__ok(self):
        self.initialize()
        for data in self.ok_message:
            self.ok_package.message_in.body = data
            package = self.trace_step.__call__(self.ok_package)

            self.assertEqual(
                package.status,
                Package.OK
            )

            self.assertTrue(
                'discard' in package.message_in.header
            )

            self.assertTrue(
                'errors' in package.general_info
            )

            self.assertTrue(
                'messages' in package.message_in.header
            )

            self.assertEqual(
                type(package.message_in.body),
                list
            )

            self.assertEqual(
                type(package.message_in.header['id']),
                str
            )

            self.assertEqual(
                package.desc_status,
                []
            )

            self.assertEqual(
                type(package.message_in.header),
                dict
            )

            for detail_data in data:
                detail_data = loads(detail_data)
                transaction_id = detail_data.get('data', {}).get('header', {}).get('transactionId', '')
                transaction_id = transaction_id if transaction_id else ''
                self.assertEqual(
                    package.message_in.header['id'],
                    transaction_id
                )

    def test__call__error(self):
        self.initialize()
        for data in self.error_message:
            self.error_package.message_in.body = data
            package = self.trace_step.__call__(self.error_package)

            self.assertEqual(
                package.status,
                Package.ERROR
            )

            self.assertTrue(
                package.message_in.header['messages']['messagesError'] > 0
            )

            self.assertTrue(
                package.desc_status != [] or package.desc_status != ''
            )

    @mock.patch("steps.trace_step.TraceStep.__call__")
    def test__call__error_mock(self, mock_call):
        self.initialize()
        mock_call.return_value = Package.ERROR
        self.assertEqual(
            self.trace_step.__call__(self.ok_package),
            Package.ERROR
        )
        mock_call.assert_called_once_with(self.ok_package)

    def test__call__exception(self):
        self.initialize()
        self.assertRaises(Exception, self.trace_step.__call__(self.ok_package))

    def test_initialize_package(self):
        self.initialize()
        for header in self.ok_message_header:
            self.ok_package.message_in.header = header
            self.ok_package.message_in.body = self.ok_message[0]
            self.trace_step.initialize_package(self.ok_package)
