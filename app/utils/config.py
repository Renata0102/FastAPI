from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_URL: str
    DB_USER: str
    DB_PASSWORD: str
    SECRET_KEY: str
    ACCESS_DAYS: int
    ALGORITHM: str


    class Config:
        env_file = 'app/.env'
        env_file_encoding = 'utf-8'
# print(__name__)
settings = Settings()
