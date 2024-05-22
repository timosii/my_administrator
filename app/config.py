import os
from abc import ABC
from typing import Final
from dotenv import load_dotenv

load_dotenv()

class Settings:
    BOT_TOKEN: Final = os.getenv('BOT_TOKEN', 'need to define')
    # ADMIN_ID: Final = int(os.getenv('ADMIN_ID'))
    DB_USER: Final = os.getenv('POSTGRES_USER', 'need to define')
    DB_PASSWORD: Final = os.getenv('POSTGRES_PASSWORD', 'need to define')
    DB_HOST: Final = os.getenv('POSTGRES_HOST', 'need to define')
    DB_PORT: Final = os.getenv('POSTGRES_PORT', 'need to define')
    DB_NAME: Final = os.getenv('POSTGRES_DB', 'need to define')

    @property
    def url_constructor(self):
        return f"postgresql+psycopg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

settings = Settings()
