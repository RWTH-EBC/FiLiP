import logging
from typing import Union
from pydantic import BaseSettings, Field, AnyHttpUrl, validator

class Settings(BaseSettings):
    CB_URL: AnyHttpUrl = Field(default="http://137.226.248.127:1026",
                               env=['ORION_URL', 'CB_URL', 'CB_HOST',
                                    'CONTEXTBROKER_URL', 'OCB_URL'])
    IOTA_URL: AnyHttpUrl = Field(default="http://137.226.248.127:4041",
                                 env='IOTA_URL')
    QL_URL: AnyHttpUrl = Field(default="http://137.226.248.127:8668",
                               env=['QUANTUMLEAP_URL', 'QL_URL'])
    LOGLEVEL: Union[int, str] = Field(
        title="LOGLEVEL",
        default='WARNING',
        description="Global logging level. Default is warning according "
                    "python's standard logging module",
        env=['LOG_LEVEL', 'LOGLEVEL']
    )

    @validator('LOGLEVEL', allow_reuse=True)
    def validate_loglevel(cls, value):
        if isinstance(value, str):
            value = value.upper()
            assert value in ['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG']
        elif isinstance(value, int):
            assert value in range(0, 50, 10)
        else:
            raise ValueError
        return value

    #TIMEZONE:

    class Config:
        env_file = '.env.filip'
        env_file_encoding = 'utf-8'
        case_sensitive = False

settings = Settings()
logging.basicConfig(level=settings.LOGLEVEL,
                    format='%(asctime)s - FiLiP.%(name)s - %(levelname)s: %('
                           'message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')
