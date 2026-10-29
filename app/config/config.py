
from pydantic_settings import BaseSettings, SettingsConfigDict


class Setting(BaseSettings):
    db_url:str = "postgresql://postgres:root@localhost:5432/rays"
    database: str
    db_name: str
    db_user: str
    api_url: str
    db_password: str
    secret_key: str
    algorithm: str
    model_config = SettingsConfigDict(env_file=".env")


settings = Setting()