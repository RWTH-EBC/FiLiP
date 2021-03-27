import logging
import os
from typing import Union
from pydantic import BaseSettings, Field, AnyHttpUrl, validator

class _Settings(BaseSettings):
    CB_URL: AnyHttpUrl = Field(default="http://localhost:1026",
                                env=['ORION_URL', 'CB_URL', 'CB_HOST',
                                     'CONTEXTBROKER_URL', 'OCB_URL'])
    IOTA_URL: AnyHttpUrl = Field(default="http://localhost:4041",
                                 env='IOTA_URL')
    QL_URL: AnyHttpUrl = Field(default="http://localhost:8668",
                               env=['QUANTUMLEAP_URL', 'QL_URL'])
    LOGLEVEL: Union[int, str] = Field(
        title="LOGLEVEL",
        default='WARNING',
        description="Global logging level. Default is warning according "
                    "python's standard logging module",
        env=['LOG_LEVEL', 'LOGLEVEL']
    )

    @validator('LOGLEVEL')
    def validate_loglevel(cls, v):
        if isinstance(v, str):
            v = v.upper()
            assert v in ['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG']
        elif isinstance(v, int):
            assert v in range(0, 50, 10)
        else:
            raise ValueError
        return v

    #TIMEZONE:

    class Config:
        env_file = '.env.filip'
        env_file_encoding = 'utf-8'
        case_sensitive = False

settings = _Settings()
print(settings)
logging.basicConfig(level=settings.LOGLEVEL,
                    format='%(asctime)s - FiLiP.%(name)s - %(levelname)s: %('
                           'message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')
