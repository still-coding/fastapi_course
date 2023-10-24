from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    db_url: str
    jwt_secret_key: str
    jwt_algorithm: str
    jwt_expire_minutes: int


settings = Settings()
