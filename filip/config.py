"""
Settings module to set url from .env.filip file. This can also seen as an
example for other applications such as webapp that use the library. Using
`*.env` belongs to best practices in containerized applications. Pydantic
provides a convenient and clean way to manage environments.
"""
from pydantic import BaseSettings, Field, AnyHttpUrl


class Settings(BaseSettings):
    """
    Settings class that reads environment variables from a local `.env.filip`
    file or environment variables. The `.env.filip` must be located in the
    current working directory.
    """
    CB_URL: AnyHttpUrl = Field(default="http://127.0.0.1:1026",
                               env=['ORION_URL', 'CB_URL', 'CB_HOST',
                                    'CONTEXTBROKER_URL', 'OCB_URL'])
    IOTA_URL: AnyHttpUrl = Field(default="http://127.0.0.1:4041",
                                 env='IOTA_URL')
    QL_URL: AnyHttpUrl = Field(default="http://127.0.0.1:8668",
                               env=['QUANTUMLEAP_URL', 'QL_URL'])

    minimum_orion_version: str = '3.6.0'
    class Config:
        env_file = '.env.filip'
        env_file_encoding = 'utf-8'
        case_sensitive = False


# create settings object
settings = Settings()
