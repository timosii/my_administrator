import os
from typing import Final

from dotenv import load_dotenv

load_dotenv()


class Settings:
    BOT_TOKEN: Final = os.getenv('BOT_TOKEN', 'need to define')
    DB_USER: Final = os.getenv('POSTGRES_USER', 'need to define')
    DB_PASSWORD: Final = os.getenv('POSTGRES_PASSWORD', 'need to define')
    DB_HOST: Final = os.getenv('POSTGRES_HOST', 'need to define')
    DB_PORT: Final = os.getenv('POSTGRES_PORT', 'need to define')
    DB_NAME: Final = os.getenv('POSTGRES_DB', 'need to define')
    REDIS_HOST: Final = os.getenv('REDIS_HOST', 'need to define')
    WEBAPP_HOST: Final = os.getenv('WEBAPP_HOST', 'need to define')
    DEV_ID: Final = os.getenv('DEV_ID', 'need_to_define')
    IS_TEST: Final = os.getenv('IS_TEST', 'need_to_define')
    CACHE_SHORT: Final = os.getenv('CACHE_SHORT', 'need_to_define')
    CACHE_LONG: Final = os.getenv('CACHE_LONG', 'need_to_define')
    WEBHOOK_HOST: Final = os.getenv('WEBHOOK_HOST', 'need_to_define')
    MFC_PASS: Final = os.getenv('MFC_PASS', 'need to define')
    MFC_LEADER_PASS: Final = os.getenv('MFC_LEADER_PASS', 'need to define')
    MO_PASS: Final = os.getenv('MO_PASS', 'need to define')
    MO_CONTROLER_PASS: Final = os.getenv('MO_CONTROLER_PASS', 'need to define')
    DOCS_URL: Final = os.getenv('DOCS_URL', 'need to define')
    DOCS_MFC: Final = os.getenv('DOCS_MFC', 'need to define')
    DOCS_MO: Final = os.getenv('DOCS_MO', 'need to define')

    @property
    def url_constructor(self):
        return f'postgresql+psycopg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}'


settings = Settings()
