from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    Loads environment variables from the .env file.
    """
    # Database Settings
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = ""
    DB_NAME: str = "db_A060"

    # DIFY AI Settings
    DIFY_API_KEY: str = ""
    DIFY_API_URL: str = ""

    @property
    def DATABASE_URL(self) -> str:
        """
        Constructs the SQLAlchemy database URL using the 'pymysql' driver.
        """
        return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset=utf8mb4"

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

settings = Settings()
