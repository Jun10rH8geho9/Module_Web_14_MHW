from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SQLALCHEMY_DATABASE_URL: str = "postgresql+asyncpg://postgres:123456@localhost:5432/Module_14"
    SECRET_KEY: str = "123456789"
    ALGORITHM: str = "123456789"
    MAIL_USERNAME: str = "example@example.com"
    MAIL_PASSWORD: str = "123456789"
    MAIL_FROM: str = "example@example.com"
    MAIL_PORT: int = 123456789
    MAIL_SERVER: str = "123456789"
    MAIL_FROM_NAME: str = "example@example.com"
    POSTGRES_DB: str = "Module_14"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: int = 123456
    POSTGRES_PORT: int =5432  
    REDIS_DOMAIN: str = 'localhost'
    REDIS_PORT: int = 6379
    CLOUDINARY_NAME: str = "abcdefghijklmnopqrstuvwxyz"
    CLOUDINARY_API_KEY: str = "123456789"
    CLOUDINARY_API_SECRET: str = "secret"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()