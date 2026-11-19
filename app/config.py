
# 1. Import Libraries
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# 2. Define Application Settings
class Settings(BaseSettings):
    database_hostname: str = Field(validation_alias="DB_HOST")
    database_port: int = Field(validation_alias="DB_PORT")
    database_name: str = Field(validation_alias="DB_NAME")
    database_username: str = Field(validation_alias="DB_USER")
    database_password: str = Field(validation_alias="DB_PASSWORD")
    secret_key: str = Field(validation_alias="SECRET_KEY")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

# 3. Initialize Settings
settings = Settings()
