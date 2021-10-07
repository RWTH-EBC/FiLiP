import logging
from dotenv import find_dotenv
from enum import Enum
from pydantic import AnyUrl, AnyHttpUrl, BaseSettings, Field, root_validator


def generate_servicepath():
    from uuid import uuid4
    return f'/{str(uuid4()).replace("-","")}'


class LogLevel(str, Enum):
    CRITICAL = 'CRITICAL'
    ERROR = 'ERROR'
    WARNING = 'WARNING'
    INFO = 'INFO'
    DEBUG = 'DEBUG'
    NOTSET = 'NOTSET'


class TestSettings(BaseSettings):
    """
    Settings for the test case scenarios according to pydantic's documentaion
    https://pydantic-docs.helpmanual.io/usage/settings/
    """

    LOG_LEVEL: LogLevel = Field(default=LogLevel.ERROR,
                                env=['LOG_LEVEL', 'LOGLEVEL'])

    CB_URL: AnyHttpUrl = Field(default="http://127.0.0.1:1026",
                               env=['ORION_URL',
                                    'CB_URL',
                                    'CB_HOST',
                                    'CONTEXTBROKER_URL',
                                    'OCB_URL'])

    IOTA_URL: AnyHttpUrl = Field(default="http://127.0.0.1:4041",
                                 env='IOTA_URL')

    QL_URL: AnyHttpUrl = Field(default="http://127.0.0.1:8668",
                               env=['QUANTUMLEAP_URL',
                                    'QL_URL'])

    MQTT_BROKER_URL: AnyUrl = Field(default="mqtt://127.0.0.1:1883",
                                    env=['MQTT_BROKER_URL',
                                         'MQTT_URL',
                                         'MQTT_BROKER'])

    # IF CI_JOB_ID is present it will always overwrite the service path
    CI_JOB_ID: str = Field(default=None,
                           env=['CI_JOB_ID'])

    # create service paths for multi tenancy scenario and concurrent testing
    FIWARE_SERVICE: str = Field(default='filip',
                                env=['FIWARE_SERVICE'])

    FIWARE_SERVICEPATH: str = Field(default_factory=generate_servicepath,
                                    env=['FIWARE_PATH',
                                         'FIWARE_SERVICEPATH',
                                         'FIWARE_SERVICE_PATH'])



    @root_validator()
    def generate_mutltitenancy_setup(cls, values):
        """
        Tests if the fields for multi tenancy in fiware are consistent.
        If CI_JOB_ID is present it will always overwrite the service path.
        Args:
            values: class variables

        Returns:

        """
        if values.get('CI_JOB_ID', None):
            values['FIWARE_SERVICEPATH'] = f"/{values['CI_JOB_ID']}"

        from filip.models.base import FiwareHeader
        FiwareHeader(service=values['FIWARE_SERVICE'],
                     service_path=values['FIWARE_SERVICEPATH'])

        return values

    class Config:
        env_file = find_dotenv('.env')
        env_file_encoding = 'utf-8'
        case_sensitive = False


settings = TestSettings()
print(f"Running tests with the following settings: \n "
      f"{settings.json(indent=2)}")

# Configure logging for all tests
logging.basicConfig(
    level=settings.LOG_LEVEL.value,
    format='%(asctime)s %(name)s %(levelname)s: %(message)s')
