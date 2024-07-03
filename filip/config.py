"""
Settings module to set url from .env.filip file. This can also seen as an
example for other applications such as webapp that use the library. Using
`*.env` belongs to best practices in containerized applications. Pydantic
provides a convenient and clean way to manage environments.
"""
import glob
import git

from pydantic import Field, AnyHttpUrl, AliasChoices
from pydantic_settings import BaseSettings, SettingsConfigDict


REPO_PATH = git.Repo('.', search_parent_directories=True)
ENV_FILIP_PATH = glob.glob(pathname='**\\.env.filip',
                           recursive=True,
                           root_dir=REPO_PATH.working_tree_dir,
                           include_hidden=True)


class Settings(BaseSettings):
    """
    Settings class that reads environment variables from a local `.env.filip`
    file or environment variables. The `.env.filip` can be located anywhere
    in the FiLiP repository.
    """
    model_config = SettingsConfigDict(env_file=f'{REPO_PATH.working_tree_dir}\\{ENV_FILIP_PATH[0]}',
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


# create settings object
settings = Settings()
