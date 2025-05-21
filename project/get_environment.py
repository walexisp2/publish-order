"""Clase para obtener variables de entorno"""
import os
import sys
from json import loads

from ant_env import Environment


class GetEnvironment:
    """Clase para obtener variables de entorno"""

    @classmethod
    def get_mapping(cls, local=False):
        if local:
            return cls.get_mapping_local()
        return cls.get_mapping_production()

    @staticmethod
    def get_mapping_production():
        """------ Obtener parametros de configuración ------"""
        try:
            error, desc_error, config = Environment().get_json(
                'SOURCE_RABBIT',
                'FILTERS',
                'GENERAL',
                'TARGET_IBMMQ',
                'TRACEABILITY',
                'RABBITMQ_TRACE'
            )
            if error:
                print('error obteniendo configmap', desc_error)
                sys.exit()
            config['SOURCE_RABBIT']['password'] = os.getenv('PASSWORD_RABBIT')
            config['RABBITMQ_TRACE']['password'] = os.getenv('PASSWORD_RABBIT_ELK')
            config['TARGET_IBMMQ']['password'] = os.getenv('PASSWORD_IBMMQ')
            return config

        except Exception as env_error:
            print('Error al obtener los parametros:', env_error)
            sys.exit()

    @staticmethod
    def get_mapping_local():
        """Obtiene los parámetros del ambiente local para desarrollo"""
        with open('config/config.json') as file:
            config = loads(file.read())
            return config
