"""
Settings module to set url from .env.filip file. This can also seen as an
example for other applications such as webapp that use the library. Using
`*.env` belongs to best practices in containerized applications. Pydantic
provides a convenient and clean way to manage environments.
"""
from pydantic import Field, AnyHttpUrl, AliasChoices, AnyUrl
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
import os
from dotenv import find_dotenv
ROOT_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), '..'))


class Settings(BaseSettings):
    """
    Settings class that reads environment variables from a local `.env.filip`
    file or environment variables. The `.env.filip` can be located anywhere
    in the FiLiP repository.
    """
    model_config = SettingsConfigDict(env_file=find_dotenv(Path(ROOT_DIR) / '.env.filip'),
                                      env_file_encoding='utf-8',
                                      case_sensitive=False, extra="ignore")

    CB_URL: AnyHttpUrl = Field(default="http://127.0.0.1:1026",
                               validation_alias=AliasChoices(
                                   'ORION_URL', 'CB_URL', 'CB_HOST',
                                   'CONTEXTBROKER_URL', 'OCB_URL'))

    IOTA_URL: AnyHttpUrl = Field(default="http://127.0.0.1:4041",
                                 validation_alias='IOTA_URL')

    QL_URL: AnyHttpUrl = Field(default="http://127.0.0.1:8668",
                               validation_alias=AliasChoices('QUANTUMLEAP_URL', 'QL_URL'))

    MQTT_BROKER_URL: AnyUrl = Field(default="mqtt://127.0.0.1:1883",
                                    validation_alias=AliasChoices(
                                        'MQTT_BROKER_URL',
                                        'MQTT_URL',
                                        'MQTT_BROKER'))

# create settings object
settings = Settings()
