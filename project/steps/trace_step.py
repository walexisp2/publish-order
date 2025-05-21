"""
Módulo de transformación de los datos provenientes de RabbitMQ.
"""
from json import loads

from ant_py import Step, Package, Error


class TraceStep(Step):
    """
    Clase de transformación de los datos de entrada en la estructura requerida
    para la trazabilidad.

    Inherits: Step
    """
    # Constantes
    INVALID_STRUCTURE = 'Invalid message structure: {}'
    EMPTY_MESSAGE = 'Empty message'

    def __call__(self, package: Package) -> Package:
        """
        Transformación de los datos de entrada en la estructura requerida
        para la trazabilidad.

        Parameters:
        -----------
        package: Package
            Paquete con la información completa del mensaje de entrada.

        Returns:
        --------
        package: Package
            Paquete con los mensajes transformado en la estructura requerida para la trazabilidad.
        """
        # Inicializa los valores del Package
        self.initialize_package(package)

        try:
            # Valida si hay datos en el mensaje de entrada
            if package.message_in.body:
                # Recorre la data de entrada
                for data in package.message_in.body:
                    # Agrega la data con la estructura requerida para la trazabilidad
                    data = loads(data)
                    package.message_in.body = [
                        {
                            'data': [data]
                        }
                    ]
                    # Obtiene id de la transacción
                    transaction_id = data.get('data', {}).get('header', {}).get('transactionId', '')
                    package.message_in.header['id'] = transaction_id
            else:
                # Envía el mensaje de error a la excepción
                raise ValueError(self.EMPTY_MESSAGE)

            # Asigna el valor de la cantidad de los mensajes de entrada
            package.message_in.header['messages']['messagesIn'] = len(package.message_in.body)

        except Exception as detail_error:
            # Envío del error
            package.message_in.header['messages']['messagesError'] += 1
            error = Error()
            error.type = error.TECNICAL
            error.body.append([self.INVALID_STRUCTURE.format(str(detail_error))])
            package.errors.append(error)
            package.status = package.ERROR
            package.desc_status = [self.INVALID_STRUCTURE.format(str(detail_error))]

        return package

    @staticmethod
    def initialize_package(package: Package):
        """
        Inicializa los valores del Package.

        Parameters:
        -----------
        package: Package
            Paquete con la información completa del mensaje de entrada.
        """
        # Establece el estado del Package
        package.general_info['errors'] = 0
        package.status = Package.OK
        package.desc_status = []

        # Establecer contadores de control del mensaje
        package.message_in.header['messages'] = {
            'messagesIn': 0,
            'messagesOut': 0,
            'messagesFilter': 0,
            'messagesError': 0
        }

        # Establecer los campos por los que se descarta/filtra los mensajes
        package.message_in.header['discard'] = {
            'orderStatusCode': 0,
            'isOnHold': 0,
            'cancelReason': 0,
            'ShipFrom/ToLocaltionId': 0
        }
