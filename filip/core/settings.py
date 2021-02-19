from pydantic import BaseSettings, Field, AnyHttpUrl

class _Settings(BaseSettings):
    OCB_URL: AnyHttpUrl = Field(default="http://localhost:1026",
                                env=['ORION_URL', 'OCB_URL'])
    IOTA_URL: AnyHttpUrl = Field(default="http://localhost:4041",
                                 env='IOTA_URL')
    QL_URL: AnyHttpUrl = Field(default="http://localhost:8668",
                               env=['QUANTUMLEAP_URL', 'QL_URL'])

    class Config:
        env_file = '../../.env'
        env_file_encoding = 'utf-8'
        case_sensitive = False


settings = _Settings()