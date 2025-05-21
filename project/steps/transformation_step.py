"""
Módulo de transformación de los datos para el destino de SINCO (cola de IBM WebSphere MQ).
"""
from ant_py import Step, Package, Error


class TransformationStep(Step):
    """
    Transforma los datos de entrada en la estructura requerida en el destino.

    Inherits: Step
    """
    def __init__(self, **args):
        """
        Método constructor.
        """
        super().__init__(**args)
        # Inicializar variables
        self.config = args

    def __call__(self, package: Package) -> Package:
        """
        Transforma los mensajes en la estructura de SINCO.

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
        response, response_blocks, count_messages_blocks = [], '', 0
        try:
            # Recorre la data de entrada
            for data in package.message_in.body:
                # Agrega los bloques del mensaje de salida para el destino
                response_blocks += self.set_structure(data)
                count_messages_blocks += 1
                # Agrupa en bloques los mensajes para el destino
                if count_messages_blocks == self.config.get('blocks', 100):
                    package.message_in.header['messages']['messagesOut'] += count_messages_blocks
                    response.append(response_blocks)
                    count_messages_blocks = 0
                    response_blocks = ''
            # Agrupa los bloques restantes para el destino
            if response_blocks:
                package.message_in.header['messages']['messagesOut'] += count_messages_blocks
                response.append(response_blocks)

            # Asigna los valores para la cantidad de mensajes de salida
            package.message_in.header['messages']['messagesBlocks'] = len(response)

        except Exception as detail_error:
            # Asigna el mensaje de salida del Package
            response = []
            package.message_in.header['messages']['messagesOut'] = 0
            # Envío del error
            package.message_in.header['messages']['messagesError'] += 1
            error = Error()
            error.type = error.TECNICAL
            error.body.append([detail_error])
            package.errors.append(error)
            package.status = package.ERROR
            package.desc_status = [detail_error]

        # Asigna el body del Package
        package.message_in.body = response

        return package

    def set_structure(self, data):
        """
        Construye el mensaje que se enviará al destino.

        Parameters:
        -----------
        data: dict
            Mensaje con la estructura de los campos requeridos para el destino.

        Returns:
        --------
        structure: str
            Mensaje con la estructura requerida para destino.
        """
        structure = ''

        structure += self.convert_str(data.get('OrderId', '')).ljust(50)
        structure += self.convert_str(data.get('OrderTypeId', '')).ljust(50)
        structure += self.convert_str(data.get('UpdatedTimestamp', '')[:17]).rjust(17, '0')
        structure += self.convert_str(data.get('SellingLocationId', '')).rjust(4, '0')
        structure += self.convert_str(data.get('IsConfirmed', '')).lower().ljust(5)
        structure += self.convert_str(data.get('DeliveryMethodId', '')).ljust(50)
        structure += self.convert_str(data.get('ReleaseId', '')).ljust(50)
        structure += self.convert_str(
            data.get('IntegerCancelledQuantityRelease', 0)
        ).rjust(10, '0')
        structure += self.convert_str(
            data.get('DecimalCancelledQuantityRelease', 0)
        ).ljust(4, '0')
        structure += self.convert_str(
            data.get('IntegerFulfilledQuantityRelease', 0)
        ).rjust(10, '0')
        structure += self.convert_str(
            data.get('DecimalFulfilledQuantityRelease', 0)
        ).ljust(4, '0')
        structure += self.convert_str(
            data.get('IntegerQuantityRelease', 0)
        ).rjust(10, '0')
        structure += self.convert_str(
            data.get('DecimalQuantityRelease', 0)
        ).ljust(4, '0')
        structure += self.convert_str(data.get('ItemId', '')).rjust(7, '0')
        structure += (
            self.convert_str(data.get('MinFulfillmentStatusId', '')).rjust(10, '0')
        )
        structure += self.convert_str(data.get('OrderLineId', '')).rjust(6, '0')
        structure += self.convert_str(
            data.get('IntegerQuantity', 0)
        ).rjust(10, '0')
        structure += self.convert_str(
            data.get('DecimalQuantity', 0)
        ).ljust(4, '0')
        structure += self.convert_str(data.get('ShipFromLocationId', '')).ljust(16)
        structure += self.convert_str(data.get('ParentOrderId', '')).ljust(50)
        structure += self.convert_str(data.get('IsReturn', '')).lower().ljust(5)
        structure += self.convert_str(data.get('ShipToLocationId', '')).ljust(16)
        structure += self.convert_str(data.get('ItemConditionId', '')).ljust(50)
        structure += self.convert_str(data.get('ReturnReason', '')).rjust(50)
        structure += self.convert_str(data.get('ProductType', '')).rjust(5, '0')
        structure += self.convert_str(data.get('SellingChannelId', '')).ljust(30)
        structure += self.convert_str(data.get('OrderCapturedDttm', ''))[:8].rjust(8, '0')
        structure += self.convert_str(data.get('OrderCapturedDttm', ''))[8:17].rjust(9, '0')
        structure += self.convert_str(data.get('NoOfDeliveryLines', '')).rjust(6, '0')
        structure += self.convert_str(data.get('CustomerFullName', '')).ljust(100)
        structure += self.convert_str(data.get('CustomerId', '')).ljust(20)
        structure += self.convert_str(data.get('CustomerPhone', '')).ljust(20)
        structure += self.convert_str(data.get('City', '')).ljust(50)
        structure += self.convert_str(data.get('PostalCode', '')).ljust(10)
        structure += self.convert_str(data.get('State', '')).ljust(50)
        structure += self.convert_str(data.get('Country', '')).ljust(50)
        structure += self.convert_str(data.get('Address', '')).ljust(150)
        structure += self.convert_str(data.get('RequestedDeliveryDate', ''))[:8].rjust(8, '0')
        structure += self.convert_str(data.get('TicketNumber', '')).ljust(20)
        structure += self.convert_str(data.get('POSTransactionId', '')).rjust(6, '0')
        structure += self.convert_str(data.get('TerminalId', '')).rjust(3, '0')
        structure += self.convert_str(data.get('DeliveryMethodSubType', '')).ljust(50)
        structure += self.convert_str(data.get('PackageDetailId', '')).ljust(20)
        structure += self.convert_str(data.get('Notes', '')).ljust(150)
        structure += self.convert_str(data.get('DateTime', ''))[:8].rjust(8, '0')
        structure += self.convert_str(data.get('DateTime', ''))[8:16].rjust(8, '0')

        return structure

    @staticmethod
    def convert_str(field):
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
        return str(field) if field not in (None, '') else ''
