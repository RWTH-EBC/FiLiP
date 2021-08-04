import logging
from typing import Union
from pydantic import BaseSettings, Field, AnyHttpUrl, validator


class Settings(BaseSettings):
    CB_URL: AnyHttpUrl = Field(default="http://127.0.0.1:1026",
                               env=['ORION_URL', 'CB_URL', 'CB_HOST',
                                    'CONTEXTBROKER_URL', 'OCB_URL'])
    IOTA_URL: AnyHttpUrl = Field(default="http://127.0.0.1:4041",
                                 env='IOTA_URL')
    QL_URL: AnyHttpUrl = Field(default="http://127.0.0.1:8668",
                               env=['QUANTUMLEAP_URL', 'QL_URL'])

    class Config:
        env_file = '.env.filip'
        env_file_encoding = 'utf-8'
        case_sensitive = False


settings = Settings()
