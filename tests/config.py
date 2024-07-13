import os
from typing import Final

from dotenv import load_dotenv

load_dotenv()


class Settings:
    TEST_ID_MFC: Final = os.getenv('TEST_ID_MFC', 'need_to_define')
    TEST_ID_MO: Final = os.getenv('TEST_ID_MO', 'need_to_define')


settings_test = Settings()
