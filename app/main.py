
# 1. Import Libraries
from fastapi import FastAPI
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from . import models
from .database import engine
from .routers import post, user, auth

# 2. Define Application Settings
class Settings(BaseSettings):
    database_password: str = Field(validation_alias="DB_PASSWORD")
    database_username: str = Field(validation_alias="DB_USER")
    secret_key: str = Field(validation_alias="SECRET_KEY")

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

# 3. Initialize Settings
settings = Settings()

# 4. Create Database Tables
models.Base.metadata.create_all(bind=engine)

# 5. Initialize FastAPI
app = FastAPI()

# 6. Include API Routers
app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(vote.router)

# 7. GET - Root Endpoint
@app.get("/")
def root():
    return {"message": "Hello World"}
