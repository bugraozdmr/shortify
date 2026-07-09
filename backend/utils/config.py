import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Veritabanı
    DB_USER = os.getenv("DATABASE_USER", "root")
    DB_PASS = os.getenv("DATABASE_PASS", "")
    DB_HOST = os.getenv("DATABASE_HOST", "localhost")
    DB_PORT = os.getenv("DATABASE_PORT", "3306")
    DB_NAME = os.getenv("DATABASE_NAME", "shortify")
    DATABASE_URL = f"mysql+aiomysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    
    # Redis
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # Uygulama Modu
    APP_TYPE = os.getenv("APP_TYPE", "DEVELOPMENT").upper()

    # Eğer istenirse daha fazla env değişkeni buraya eklenebilir.
    @staticmethod
    def get(key: str, default=None):
        return os.getenv(key, default)

config = Config()
