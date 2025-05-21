"""
Módulo de validación de los datos provenientes de la cola de RabbitMQ.
"""
import re
from json import loads

from ant_validator import Validator
from ant_py import Step, Package, Error


class ValidationStep(Step):
    """
    Clase para validar los datos de entrada con respecto al destino.

    Inherits: Step
    """
    # Constantes
    FILTER_CANCEL_REASON = ['3000']
    CHARACTERS_WITH_ACCENTS = 'áéíóúüñÁÉÍÓÚÜÑ'
    CHARACTERS_WITHOUT_ACCENTS = 'aeiouunAEIOUUN'
    MSG_NUMBER_ERROR = 'Message #: {}: {}'
    EMPTY_PUBLISH_ORDER = 'Empty Publish Order'
    INVALID_STRUCTURE = 'Invalid message structure: {}'
    ERROR_GETTING_DATA = 'Error getting data from source to destination'

    def __init__(self, **args):
        """
        Método constructor.
        """
        super().__init__(**args)
        # Inicializar variables
        self.config = args
        self.error_blocks = []

        # Lectura de archivo de configuración para la validación de los mensajes
        with open('config/message.cnf') as file_config:
            self.validate_data = loads(file_config.read())

    def __call__(self, package: Package) -> Package:
        """
        Valída los datos de entrada para el mensaje destino.

        Parameters:
        -----------
        package: Package
            Paquete con la información completa del mensaje de entrada.

        Returns:
        --------
        package: Package
            Paquete con los mensajes transformado en la estructura requerida para el destino.
        """
        # Establecer variables
        response = []

        # Asigna los mensajes de entrada
        package.message_in.header['messages']['messagesIn'] = 0

        try:
            # Valida si hay errores del step anterior
            if not package.message_in.header['messages']['messagesError']:
                # Recorre la data de entrada
                for data in package.message_in.body[0]['data']:
                    # Obtiene la información del Publish Order
                    publish_order = (
                        data.get('data', {}).get('data', {}).get('publishOrderDto', {})
                    )

                    # Procesa la información del mensaje de entrada
                    self.process_data(
                        publish_order,
                        response,
                        package
                    )
            # Empaqueta los errores en el Package Error
            if len(self.error_blocks) > 0:
                error = ",".join(self.error_blocks)
                raise Exception(error)

        except Exception as detail_error:
            # Envío del error
            package.message_in.header['messages']['messagesError'] += 1
            # Asigna el mensaje de salida del Package
            package.message_in.header['messages']['messagesOut'] = 0

            error = Error()
            desc = f'{error.funcname}: {error.source} - {detail_error}'
            error.type = error.TECNICAL
            error.body = [desc]
            package.errors.append(error)
            package.desc_status = [detail_error]
            if len(response) == 0:
                package.status = package.ERROR
        # Asigna el body del Package
        package.message_in.body = sorted(response, key=lambda detail: detail['UpdatedTimestamp'])
        # Limpieza los errores
        self.error_blocks = []

        return package

    def process_data(self, publish_order: dict, response: list, package: Package):
        """
        Procesa y valida los datos de entrada.

        Parameters:
        -----------
        publish_order: dict
            Diccionario que contiene la información del Publish Order.
        Response: list
            Mensaje con la data de salida.
        Package: Package
            Paquete con la información completa del mensaje de entrada.
        """
        if publish_order:
            order_lenght = len(publish_order.get('orderLineList', []))
            # Recorre la lista del Order Line para obtener los datos
            for order_line in publish_order.get('orderLineList', []):
                # Obtiene la lista releaseList
                release_list = publish_order.get('releaseList')
                plus_to_send = []
                if release_list:
                    # Obtiene los valores para el Release al hacer match la Orden con el Release
                    plus_to_send = self.match_order_line_with_release_line(
                        publish_order,
                        order_line,
                        release_list,
                        order_lenght
                    )
                # Asigna los valores por defecto si el releaseList no tiene información
                for data in plus_to_send:
                    if not data.get('releaseId'):
                        data['releaseId'] = ''
                        data['releaseLine'] = {}
                        data['orderLine'] = order_line

                # Cuenta los mensajes de entrada
                package.message_in.header['messages']['messagesIn'] += 1
                # Obtiene la estructura del con los mensajes requeridos para el destino
                structures = self.set_structure(
                    plus_to_send,
                    order_line,
                    package
                )
                # Valída los campos para el mensaje destino
                self.structure_validation(
                    structures,
                    response,
                    package
                )

                # Asigna el releaseId para la proxima búsqueda
                for data in plus_to_send:
                    data['releaseId'] = ''

        else:
            # Cuenta los mensajes de entrada
            package.message_in.header['messages']['messagesIn'] += 1
            # Envía el detalle del error a la excepción general
            raise ValueError(self.INVALID_STRUCTURE.format(self.EMPTY_PUBLISH_ORDER))

    def set_structure(self, plus_to_send: list, order_line: dict, package: Package) -> list:
        """
        Mapea los datos necesarios para el destino y se agregan a una
        estructura depurada.

        Parameters:
        -----------
        data: dict
            Diccionario que contiene la información del Publish Order.
        Order_line: dict
            Diccionario con la información del Order Line.
        Package: Package
            Paquete con la información completa del mensaje de entrada.

        Returns:
        --------
        structure: dict
            Mensaje con la estructura de los campos requeridos para el destino.
        """
        structures = list()
        try:
            # Establecer variables
            # Obtiene el campo minFulfillmentStatusId sin puntos
            order_line['minFulfillmentStatusId'] = (
                order_line.get('minFulfillmentStatusId', '').replace('.', '')
            )

            # Valída que el estado del evento de la orden sea válido
            if order_line['minFulfillmentStatusId'] in self.config['filters']:
                if not (
                        order_line['minFulfillmentStatusId'] in self.FILTER_CANCEL_REASON
                        and order_line.get('cancelReason')
                ):
                    structures = self.build_structure(plus_to_send, order_line)
                else:
                    # Cuenta los mensajes descartados
                    package.message_in.header['discard']['cancelReason'] += 1
                    package.message_in.header['messages']['messagesFilter'] += 1
            else:
                # Cuenta los mensajes descartados
                package.message_in.header['discard']['orderStatusCode'] += 1
                package.message_in.header['messages']['messagesFilter'] += 1
        except Exception as set_structure_exception:
            pass

        return structures

    def build_structure(self, plus_to_send: list, order_line: dict) -> list:
        """
        Construye la estructura con los campos requeridos para el estado de las órdenes.

        Parameters:
        -----------
        data: dict
            Data con la información de los Items(PLUS) de la Orden.
        Message_position: int
            Posición del mensaje.

        Returns:
        --------
        structure: dict
            Mensaje con la estructura de los campos requeridos para el destino de las órdenes.
        """
        # Establece los campos para la estructura del destino
        structures = list()
        for data in plus_to_send:
            structure = {
                'OrderId': order_line.get('orderId', ''),
                'OrderTypeId': data.get('orderTypeId', ''),
                'UpdatedTimestamp': self.format_datetime(
                    self.convert_str(order_line.get('updatedTimestamp'))[:30]
                ),
                'SellingLocationId': data.get('sellingLocationId', ''),
                'IsConfirmed': data.get('isConfirmed', ''),
                'DeliveryMethodId': order_line.get('deliveryMethodId', ''),
                'ItemId': data.get('releaseLine').get('itemId'),
                'MinFulfillmentStatusId': data.get('orderLine').get('minFulfillmentStatusId', '').replace('.', ''),
                'OrderLineId': order_line.get('orderLineId', ''),
                'IntegerQuantity': '',
                'DecimalQuantity': '',
                'IsOnHold': data.get('isOnHold', False),
                'ParentOrderId': order_line.get('parentOrderId', ''),
                'IsReturn': order_line.get('isReturn', False),
                'ShipToLocationId': order_line.get('shipToLocationId', ''),
                'ItemConditionId': '',
                'ReturnReason': '',
                'SellingChannelId': data.get('sellingChannelId', ''),
                'OrderCapturedDttm': self.format_datetime(
                    self.convert_str(data.get('orderCapturedDttm'))[:30]
                ),
                'CustomerFullName': '',
                'CustomerId': data.get('customerId', ''),
                'CustomerPhone': data.get('customerPhone', ''),
                'City': '',
                'PostalCode': '',
                'State': '',
                'Country': '',
                'Address': '',
                'RequestedDeliveryDate': self.format_datetime(
                    self.convert_str(data.get('requestedDeliveryDate'))[:30]
                ),
                'TicketNumber': self.convert_int(data.get('ticketNumber', '')),
                'POSTransactionId': self.convert_int(data.get('POSTransactionId', '')),
                'TerminalId': self.convert_int(data.get('terminalId', '')),
                'DeliveryMethodSubType': order_line.get('deliveryMethodSubType', ''),
                'ProductType': '',
                'Notes': '',
                'DateTime': self.format_datetime(
                    self.convert_str(data.get('dateTime'))[:30]
                )
            }

            try:
                # Obtiene los campos requeridos para el destino
                order_line_additional = self.validate_dict(order_line.get('orderLineAdditional'))
                ship_to_address = self.validate_dict(order_line.get('orderLineShipToAddress'))

                structure['ItemConditionId'] = order_line_additional.get('itemConditionId', '')
                structure['ReturnReason'] = order_line_additional.get('returnReason', '')
                structure['City'] = ship_to_address.get('city', '')
                structure['PostalCode'] = ship_to_address.get('postalCode', '')
                structure['State'] = ship_to_address.get('state', '')
                structure['Country'] = ship_to_address.get('country', '')
                structure['Address'] = self.concat_address(ship_to_address)
                structure['Notes'] = self.concat_notes(
                    self.validate_list(order_line.get('orderLineNoteList'))
                )
                structure['CustomerFullName'] = '{} {}'.format(
                    data.get('customerFirstName', ''),
                    data.get('customerLastName', '')
                )
                structure['ProductType'] = self.validate_dict(
                    order_line.get('orderLinePromisingInfo')
                ).get('productType', '')

                # Valída si es una cancelación (9000) de la orden
                if structure['MinFulfillmentStatusId'] == '9000':
                    # Recorre la lista para obtener la cantidad de PLUS cancelados
                    for order_line_cancel in order_line.get('orderLineCancelHistory', []):
                        structure['IntegerQuantity'], structure['DecimalQuantity'] = (
                            self.remove_decimal_point(order_line_cancel.get('cancelQuantity'))
                        )
                else:
                    # Obtiene la parte entera y la parte decimal de la cantidad separados
                    structure['IntegerQuantity'], structure['DecimalQuantity'] = (
                        self.remove_decimal_point(order_line.get('quantity'))
                    )

                    # Validación para obtener el valor inicial del ShipFromLocationId
                    structure['ShipFromLocationId'] = (
                        '0000' if bool(structure.get('IsReturn'))
                        else self.convert_str(data.get('shipFromLocationId'))
                    )
                    # Obtiene el valor del campo ShipFromLocationId
                    self.get_ship_from_location_id(
                        structure,
                        order_line
                    )

                # Recorre la lista para obtener los datos del Released
                if len(data['releaseLine']) > 0:
                    structure['ReleaseId'] = data.get('releaseId', '')
                    release_line = data.get('releaseLine', {})

                    cancelled_quantity_release = self.remove_decimal_point(
                        release_line.get('cancelledQuantity')
                    )
                    fulfilled_quantity_release = self.remove_decimal_point(
                        release_line.get('fulfilledQuantity')
                    )
                    quantity_release = self.remove_decimal_point(
                        release_line.get('quantity')
                    )
                    structure['IntegerCancelledQuantityRelease'] = cancelled_quantity_release[0]
                    structure['DecimalCancelledQuantityRelease'] = cancelled_quantity_release[1]
                    structure['IntegerFulfilledQuantityRelease'] = fulfilled_quantity_release[0]
                    structure['DecimalFulfilledQuantityRelease'] = fulfilled_quantity_release[1]
                    structure['IntegerQuantityRelease'] = quantity_release[0]
                    structure['DecimalQuantityRelease'] = quantity_release[1]
                    structure['NoOfDeliveryLines'] = release_line.get('noOfDeliveryLines', '')
                    structure['PackageDetailId'] = release_line.get('packageDetailId', '')
                structures.append(structure)
            except Exception as build_structure_exception:
                pass
        return structures

    def structure_validation(self, structures: list, response: list, package: Package):
        """
        Validad la estructura del mensaje.

        Parameters:
        -----------
        structure: dict
            Contiene la estructura a validar.
        Response: list
            Mensaje con la data de salida.
        Package: Package
            Paquete con la información completa del mensaje de entrada.
        """
        # Valída que existan datos para el mensaje destino
        for structure in structures:
            if structure:
                if str(structure.get('ShipFromLocationId', '')).upper() in self.config['filter_ship_from'] \
                        or str(structure.get('ShipToLocationId', '')).upper() in self.config['filter_ship_to']:
                    valid, description = False, ''
                    package.message_in.header['discard']['ShipFrom/ToLocaltionId'] += 1
                    package.message_in.header['messages']['messagesFilter'] += 1
                else:
                    if structure.get('ShipFromLocationId') == "":
                        structure['ShipFromLocationId'] = "0000"
                    valid, description = Validator.validate_data(
                        self.validate_data, structure
                    )
            else:
                valid, description = False, [self.INVALID_STRUCTURE.format(self.ERROR_GETTING_DATA)]

            # Valída que la estructura del mensaje validado sea correcto
            if valid:
                # Valída que el estado de la Orden y el campo Is On Hold cumplan con los filtros
                valid_code = self.code_validation(
                    structure['IsOnHold'], structure.get('MinFulfillmentStatusId')
                )
                if valid_code:
                    # Agrega la data para el destino
                    response.append(structure)
                else:
                    # Cuenta los mensajes descartados
                    package.message_in.header['discard']['isOnHold'] += 1
                    package.message_in.header['messages']['messagesFilter'] += 1
            elif package.message_in.header['messages']['messagesFilter'] == 0:
                # Cuenta y agrega los mensajes de Error
                package.message_in.header['messages']['messagesError'] += 1
                self.add_error(description, package.message_in.header['messages']['messagesIn'])

    def match_order_line_with_release_line(
            self, publish_order: dict, order_line: dict, release_list: dict, order_length: int
    ):
        """
        Recorre y obtiene los campos de cada Orden con su respectivo Release.

        Parameters:
        -----------
        data: dict
            Data con los campos requeridos para el mensaje destino.
        Publish_order: dict
            Data con los campos de la estructura del Publish Order.
        Order_line: dict
            Data con los campos de la estructura del Order Line.
        Release_list: dict
            Data con los campos de la estructura del Release List.
        """
        plus_to_send = []
        # Recorre cada uno de items que hay en el releaseList
        for idx, release in enumerate(release_list):
            for idy, release_line in enumerate(release.get('releaseLineList', [])):
                data = {
                    'orderTypeId': publish_order.get('orderTypeId', ''),
                    'isConfirmed': publish_order.get('isConfirmed', False),
                    'isOnHold': publish_order.get('isOnHold', False),
                    'sellingLocationId': publish_order.get('sellingLocationId', ''),
                    'sellingChannelId': publish_order.get('sellingChannelId', ''),
                    'orderCapturedDttm': publish_order.get('orderCapturedDttm', ''),
                    'customerFirstName': publish_order.get('customerFirstName', ''),
                    'customerLastName': publish_order.get('customerLastName', ''),
                    'customerId': publish_order.get('customerId', ''),
                    'customerPhone': publish_order.get('customerPhone', ''),
                    'requestedDeliveryDate': publish_order.get('requestedDeliveryDate', ''),
                    'ticketNumber': publish_order.get('ticketNumber', ''),
                    'POSTransactionId': publish_order.get('POSTransactionId', ''),
                    'terminalId': publish_order.get('terminalId', ''),
                    'dateTime': publish_order.get('dateTime', ''),
                    'shipFromLocationId': release.get('shipFromLocationId', '')
                }
                # Compara que los campos itemId, orderLineId y quantity del Order Line
                # hagan match con los del Release Line
                if release_line.get('cancelledQuantity') == release_line.get('quantity'):
                    if order_line.get('itemId') == release_line.get('itemId'):
                        data['releaseId'] = release.get('releaseId', '')
                        data['releaseLine'] = release_line
                        data['orderLine'] = order_line.copy()
                        data['orderLine']['minFulfillmentStatusId'] = '9001'
                        plus_to_send.append(data)
                elif release_line.get('quantityDetail'):
                    try:
                        quantity_status = release_line.get('quantityDetail', {}).get('quantityStatus', [])
                    except:
                        quantity_status = None
                    if quantity_status:
                        if ((quantity_status[0]['changed'] is True) or
                                (quantity_status[0]['changed'] is False and quantity_status[0]['statusId'] == "3000") or
                                (release_line.get('cancelledQuantity') == quantity_status[0]['quantity'])):
                            if release_line.get('cancelledQuantity') == quantity_status[0]['quantity']:
                                release_line['quantityDetail']['quantityStatus'][0]['statusId'] = "9001"
                            if order_line.get('itemId') == release_line.get('itemId'):
                                data['releaseId'] = release.get('releaseId', '')
                                data['releaseLine'] = release_line
                                data['orderLine'] = order_line.copy()
                                if quantity_status[0]['statusId'] != '3000' and quantity_status[0]['changed'] is True:
                                    order_line['minFulfillmentStatusId'] = quantity_status[0]['statusId'].replace('.', '')
                                    data['orderLine']['minFulfillmentStatusId'] = order_line['minFulfillmentStatusId']
                                plus_to_send.append(data)
                else:
                    if order_line.get('minFulfillmentStatusId') == '7000':
                        release_line['quantity'] = release_line.get('fulfilledQuantity')
                        if release_line['quantity'] > 0.0:
                            data['shipFromLocationId'] = release.get('shipFromLocationId')
                    if (
                            order_line.get('itemId') == release_line.get('itemId') and
                            order_line.get('orderLineId') == release_line.get('orderLineId')
                            and self.convert_float(order_line.get('quantity')) ==
                            self.get_quantity(release_line)
                    ):
                        data['releaseId'] = release.get('releaseId', '')
                        data['releaseLine'] = release_line
                        data['orderLine'] = order_line
                        # Elimina del publish_order los item del release ya obtenidos
                        # para no volver a recorrerlos.
                        publish_order.get('releaseList')[idx].get('releaseLineList').pop(idy)
                        plus_to_send.append(data)
                        break
            # Si el releaseId tiene información no sigue recorriendo el release
            # if data.get('releaseId'):
            #    break
        return plus_to_send

    def get_ship_from_location_id(self, structure: dict, order_line: dict):
        """
        Obtiene el valor del campo Ship From Location Id.

        Parameters:
        -----------
        structure: dict
            Estructura con los campos requeridos para el mensaje destino.
        Order_line: dict
            Data con los campos de la estructura del Order Line.
        """
        # Obtiene el orderLineAllocationList
        order_line_allocation_list = self.validate_list(order_line.get('orderLineAllocationList'))

        # Valida si ya existe un valor para el ShipFromLocationId
        if not structure.get('ShipFromLocationId'):
            # Recorre la lista para obtener los datos de la Order Asignada
            for order_line_allocation in order_line_allocation_list:
                # Valida si la Order es de una CEDI
                if len(order_line_allocation_list) > 1:
                    # Si la orden es de un CEDI, toma el valor del Ship From Location Id
                    # donde la cantidad sea mayor a cero (0.0)
                    structure['ShipFromLocationId'] = (
                        order_line_allocation.get('shipFromLocationId', '') if
                        self.convert_float(order_line_allocation.get('quantity')) > 0.0 else
                        structure['ShipFromLocationId']
                    )
                else:
                    # Obtiene el Ship From Location Id si no es un CEDI
                    structure['ShipFromLocationId'] = (
                        order_line_allocation.get('shipFromLocationId', '')
                    )

    def add_error(self, description: list, message_number: int):
        """
        Agrega los mensajes de error.

        Parameters:
        -----------
        description: list
            Lista con la descripción de los errores del mensaje.
        Message_number: int
            Posición o número del mensaje con error.
        """
        # Recorre y obtiene los errores
        for data_error in description:
            self.error_blocks.append(self.MSG_NUMBER_ERROR.format(message_number, data_error))

    @staticmethod
    def remove_decimal_point(field) -> tuple:
        """
        Separa el valor de la parte entera y de la parte decimal de un dato numérico.

        Parameters:
        -----------
        field: str, int, float
            Campo para separar el valor de la parte entera y de la parte decimal.

        Returns:
        --------
        integer_part: str
            Campo con el valor de la parte entera del dato de entrada.
        Decimal_part: str
            Campo con el valor de la parte decimal del dato de entrada.
        """
        # Convierte el campo en entero para poder realizar las búsquedas
        field = str(field)
        # Obtiene la cantidad de dígitos de la parte entera del número
        whole_digits = field.find('.')

        # Válida si hay número en la parte entera
        if whole_digits > 0:
            # Retorna los valores de la parte entera y de la parte decimal
            return field[:whole_digits], field[whole_digits+1:]
        # Retorna los valores de la parte entera y de la parte decimal
        return field, '0'

    @staticmethod
    def convert_float(field) -> float:
        """
        Convierte y retorna el valor del campo en un valor numérico flotante (float).

        Parameters:
        -----------
        field: str, int, float
            Campo para convertir a flotante (float).

        Returns:
        --------
        field: float
            Campo convertido en flotante (float).
        """
        try:
            field = float(field)
        except Exception as convert_float_exception:
            field = 0.0
        return field

    @staticmethod
    def convert_int(field) -> int:
        """
        Convierte y retorna el valor del campo en int.

        Parameters:
        -----------
        field: str, int, float, bool
            Campo para convertir a int.

        Returns:
        --------
        field: int
            Campo convertido en int.
        """
        try:
            field = int(field)
        except Exception as convert_int_exception:
            field = 0
        return field

    @staticmethod
    def convert_str(field) -> str:
        """
        Convierte y retorna el valor del campo en un string.

        Parameters:
        -----------
        field: str, int, float, bool
            Campo para convertir a un string.

        Returns:
        --------
        field: str
            Campo convertido en un string.
        """
        return str(field) if field not in (None, 'None', '') else ''

    @staticmethod
    def validate_list(field) -> list:
        """
        Valida que sea un dato tipo diccionario.

        Parameters:
        -----------
        field: str, int, float, bool, list, dict
            Campo para validar.

        Returns:
        --------
        field: dict
            Campo validado, si no es un dato tupo dict, retorna {}.
        """
        return field if isinstance(field, list) else []

    @staticmethod
    def validate_dict(field) -> dict:
        """
        Valida que sea un dato tipo diccionario.

        Parameters:
        -----------
        field: str, int, float, bool, list, dict
            Campo para validar.

        Returns:
        --------
        field: dict
            Campo validado, si no es un dato tupo dict, retorna {}.
        """
        return field if isinstance(field, dict) else {}

    def code_validation(self, is_on_hold: bool, min_fulfillment_status_id: str) -> bool:
        """
        Valída que el estado de la Orden cumplan con las condiciones para el campo Is On Hold.

        Parameters:
        -----------
        is_on_hold: bool
            Indica si la orden se encuentra en espera (allocated).
        Min_fulfillment_status_id: str
            Código del estado de la Orden.

        Returns:
        --------
        code_validation: bool
            Retorna si las condiciones son válidas para el estado de la Orden.
        """
        return bool(
            isinstance(is_on_hold, bool) and
            is_on_hold in self.config['filters'].get(min_fulfillment_status_id, [])
        )

    @staticmethod
    def get_quantity(release_line: dict) -> float:
        """
        Obtiene el valor de la resta de las cantidades con las cantidades canceladas del
        Release Line.

        Parameters:
        -----------
        release_line: dict
            Diccionario con la información del Release Line.

        Returns:
        --------
        quantity: float
            Cantidad de la resta de las cantidades con las cantidades canceladas del Release Line
            para comparar con la del OrderLine.
        """
        try:
            quantity = (
                float(release_line.get('quantity')) - float(release_line.get('cancelledQuantity'))
            )
        except Exception as get_quantity_exception:
            quantity = 0.0
        return quantity

    def concat_notes(self, note_list: list) -> str:
        """
        Obtiene las notas y las concatena separándolas por puntos.

        Parameters:
        -----------
        note_list: list
            Lista de diccionarios con las notas a concatenar.

        Returns:
        --------
        new_note: str
            Resultado de las notas concatenadas.
        """
        # Establecer variables
        notes = []

        # Recorre las notas
        for note in note_list:
            # Obtiene las notas
            note_temp = [
                self.replace_accent(self.convert_str(note.get('noteCategoryId', ''))),
                self.replace_accent(self.convert_str(note.get('noteTypeId', ''))),
                self.replace_accent(self.convert_str(note.get('noteText', '')))
            ]
            # Agrega las notas
            notes.append('.'.join(note_temp))

        # Separa por - si hay más de una nota
        note = self.convert_str('-'.join(notes))[:150]

        # Valída los caracteres permitidos
        new_note = re.sub(
            r"[^ -z{}~]",
            "",
            note
        )

        return new_note

    def concat_address(self, ship_to_address: dict) -> str:
        """
        Obtiene la dirección y las concatena separándolas por comas.

        Parameters:
        -----------
        ship_to_address: dict
            diccionario con las direcciones.

        Returns:
        --------
        new_address: str
            Resultado de las direcciones concatenadas.
        """
        # Obtiene las direcciones del cliente
        address_temp = [
            self.replace_accent(self.convert_str(ship_to_address.get('address1', ''))),
            self.replace_accent(self.convert_str(ship_to_address.get('address2', ''))),
            self.replace_accent(self.convert_str(ship_to_address.get('address3', '')))
        ]

        # Valída los caracteres permitidos
        new_address = re.sub(
            r"[^ -z{}~]",
            "",
            self.convert_str(','.join(address_temp))[:149]
        )

        return new_address

    @staticmethod
    def replace_accent(field: str) -> str:
        """
        Reemplaza los caracteres con acento.

        Parameters:
        -----------
        field: str
            String a reemplazar los caracteres de acento.

        Returns:
        -----------
        field: str
            String con los caracteres de acento reemplazados.
        """
        replacement = str.maketrans(
            ValidationStep.CHARACTERS_WITH_ACCENTS,
            ValidationStep.CHARACTERS_WITHOUT_ACCENTS
        )
        return field.translate(replacement)

    @staticmethod
    def format_datetime(field: str) -> str:
        """
        Da formato a los campos de fecha-hora con formato de milisegundos.

        Parameters:
        -----------
        field: str
            Campo fecha-hora a validar.

        Returns:
        -----------
        field: str
            Campo fecha-hora con formato de milisegundos.
        """
        # Valída si el valor de la fecha no tiene los milisegundos
        if 0 < len(field) <= 19:
            field = f"{field}.000"
        return field
