import os
from abc import ABC
from typing import Final
from dotenv import load_dotenv

load_dotenv()

class Settings:
    BOT_TOKEN: Final = os.getenv('BOT_TOKEN', 'need to define')
    ADMIN_ID: Final = int(os.getenv('ADMIN_ID'))
    PG_USER: Final = os.getenv('POSTGRES_USER', 'need to define')
    PG_PASSWORD: Final = os.getenv('POSTGRES_PASSWORD', 'need to define')
    PG_HOST: Final = os.getenv('POSTGRES_HOST', 'need to define')
    PG_PORT: Final = os.getenv('POSTGRES_PORT', 'need to define')
    PG_DB: Final = os.getenv('POSTGRES_DB', 'need to define')

settings = Settings()
