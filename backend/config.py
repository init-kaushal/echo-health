from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    eka_api_key: str = ""
    eka_api_base_url: str = "https://uat.eka.care/api/v1"
    environment: str = "development"

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings() 