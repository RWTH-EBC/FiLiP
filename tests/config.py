import logging
from uuid import uuid4
from dotenv import find_dotenv
from pydantic import AnyUrl, AnyHttpUrl, Field, AliasChoices, model_validator
from filip.models.base import FiwareHeader, LogLevel
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Union, Optional


def generate_servicepath():
    """
    Generates a random service path

    Returns:
        String: unique service path
    """
    return f'/{str(uuid4()).replace("-", "")}'


class TestSettings(BaseSettings):
    """
    Settings for the test case scenarios according to pydantic's documentaion
    https://pydantic-docs.helpmanual.io/usage/settings/
    """
    LOG_LEVEL: LogLevel = Field(default=LogLevel.ERROR,
                                validation_alias=AliasChoices('LOG_LEVEL', 'LOGLEVEL'))

    CB_URL: AnyHttpUrl = Field(default="http://localhost:1026",
                               validation_alias=AliasChoices('ORION_URL',
                                    'CB_URL',
                                    'CB_HOST',
                                    'CONTEXTBROKER_URL',
                                    'OCB_URL'))
    LD_CB_URL: AnyHttpUrl = Field(default="http://localhost:1026",
                                  validation_alias=AliasChoices('LD_ORION_URL',
                                                                'LD_CB_URL',
                                                                'ORION_LD_URL',
                                                                'SCORPIO_URL',
                                                                'STELLIO_URL'))
    IOTA_URL: AnyHttpUrl = Field(default="http://localhost:4041",
                                 validation_alias='IOTA_URL')
    IOTA_JSON_URL: AnyHttpUrl = Field(default="http://localhost:4041",
                                      validation_alias='IOTA_JSON_URL')

    IOTA_UL_URL: AnyHttpUrl = Field(default="http://127.0.0.1:4061",
                                    validation_alias=AliasChoices('IOTA_UL_URL'))

    QL_URL: AnyHttpUrl = Field(default="http://127.0.0.1:8668",
                               validation_alias=AliasChoices('QUANTUMLEAP_URL',
                                                             'QL_URL'))

    MQTT_BROKER_URL: AnyUrl = Field(default="mqtt://127.0.0.1:1883",
                                    validation_alias=AliasChoices(
                                        'MQTT_BROKER_URL',
                                        'MQTT_URL',
                                        'MQTT_BROKER'))

    MQTT_BROKER_URL_INTERNAL: AnyUrl = Field(default="mqtt://mosquitto:1883",
                                             validation_alias=AliasChoices(
                                                 'MQTT_BROKER_URL_INTERNAL',
                                                 'MQTT_URL_INTERNAL'))

    # IF CI_JOB_ID is present it will always overwrite the service path
    CI_JOB_ID: Optional[str] = Field(default=None,
                                     validation_alias=AliasChoices('CI_JOB_ID'))

    # create service paths for multi tenancy scenario and concurrent testing
    FIWARE_SERVICE: str = Field(default='filip',
                                validation_alias=AliasChoices('FIWARE_SERVICE'))

    FIWARE_SERVICEPATH: str = Field(default_factory=generate_servicepath,
                                    validation_alias=AliasChoices('FIWARE_PATH',
                                                                  'FIWARE_SERVICEPATH',
                                                                  'FIWARE_SERVICE_PATH'))


    @model_validator(mode='after')
    def generate_multi_tenancy_setup(cls, values):
        """
        Tests if the fields for multi tenancy in fiware are consistent.
        If CI_JOB_ID is present it will always overwrite the service path.
        Args:
            values: class variables

        Returns:

        """
        if values.model_dump().get('CI_JOB_ID', None):
            values.FIWARE_SERVICEPATH = f"/{values.CI_JOB_ID}"

        # validate header
        FiwareHeader(service=values.FIWARE_SERVICE,
                     service_path=values.FIWARE_SERVICEPATH)

        return values
    model_config = SettingsConfigDict(env_file=find_dotenv('.env'),
                                      env_file_encoding='utf-8',
                                      case_sensitive=False,
                                      use_enum_values=True)


# create settings object
settings = TestSettings()
print(f"Running tests with the following settings: \n "
      f"{settings.model_dump_json(indent=2)}")

# configure logging for all tests
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format='%(asctime)s %(name)s %(levelname)s: %(message)s')
