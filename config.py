""" File with settings and configs for the project"""

from pydantic_settings import BaseSettings, SettingsConfigDict

from pydantic import PostgresDsn


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env')

    postgres: PostgresDsn


settings = Settings()