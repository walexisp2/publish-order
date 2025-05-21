"""
Módulo principal Publish Order
"""
from ant_py import Route
from ant_rabbitmq import Reader, Writer as RabbitMQWriter
from ant_ibmmq import Writer
from ant_trace import TraceSubscriber

from get_environment import GetEnvironment
from steps.trace_step import TraceStep
from steps.validation_step import ValidationStep
from steps.transformation_step import TransformationStep


def get_instances(parameters):
    """
    Instancia las clases para el proceso

    Parameters:
    ---------------------
        parameters: dict
            Parámetros de configuración de la integración

    Returns:
    ---------------------
        instances: dict
            Contiene la instancia de clases de proceso de la integración
    """
    instances = {
        "source_rabbitmq": None,
        "trace_step": None,
        "validation_step": None,
        "transformation_step": None,
        "target_ibmmq": None,
        "elk": None
    }
    try:
        instances["elk"] = TraceSubscriber(
            route="sinco-publicar-orden",
            connection=RabbitMQWriter(
                **parameters["RABBITMQ_TRACE"]
            ),
            **parameters["TRACEABILITY"]
        )
        instances["source_rabbitmq"] = Reader(
            **parameters.get("SOURCE_RABBIT")
        )
        instances["trace_step"] = TraceStep(
            name="trace_step"
        )
        instances["validation_step"] = ValidationStep(
            name='validation_step',
            filters=parameters['FILTERS'],
            filter_ship_from=parameters['GENERAL']['ship_from_location_id_filter'],
            filter_ship_to=parameters['GENERAL']['ship_to_location_id_filter']
        )
        instances["transformation_step"] = TransformationStep(
            name='transformation_step',
            blocks=parameters['GENERAL']['blocks_output']
        )
        instances["target_ibmmq"] = Writer(
            **parameters.get('TARGET_IBMMQ')
        )
    except Exception as get_instances_error:
        print(get_instances_error)

    return instances


def init_process(instances, parameters):
    """
    Instancia e inicializa el Framework de la integración

    Parameters:
    ---------------------------
        instances: dict
                Contiene las instancias de los procesos que interactuan en la integración
    Returns:
    ---------------------------
        route: ROUTE
            Instancia del Framework
    """
    route = None
    try:
        route = Route(
            name="sinco-publicar-orden",
            route_log=f"{parameters['TRACEABILITY'].get('log_dir')}/{parameters['TRACEABILITY'].get('log_file')}"
        )
        route.set_trace(instances["elk"])

        route.pipe_in().\
            source(instances["source_rabbitmq"]).\
            step(instances["trace_step"]).trace(name='message_in').\
            step(instances["validation_step"]).\
            step(instances["transformation_step"]).\
            to(instances["target_ibmmq"])

        route.pipe_out().trace(name='message_out')

    except Exception as init_process_error:
        print(init_process_error)
    return route


# ------ Proceso ------
try:
    PARAMETERS = GetEnvironment.get_mapping()
    ROUTE = init_process(
        get_instances(
            PARAMETERS
        ),
        PARAMETERS
    )
except Exception as detail_error:
    print(detail_error)

if __name__ == '__main__':
    ROUTE.start_parallel(PARAMETERS['GENERAL'].get('start_parallel', 1))
