import os
from dataclasses import dataclass

from aiogram import Bot
from aiogram.types import File
from loguru import logger

from app.config import settings


@dataclass
class PhotoForSave:
    photo_id: str

    def get_photo_path(self):
        path = os.path.join(
            settings.DATA_PATH,
            f'{self.photo_id}.jpg'
        )
        return path


class PhotoSaver:
    def __init__(
            self,
            photo: str,
    ):
        self.photo = PhotoForSave(photo)

    async def download_photo(self, bot: Bot):
        photo_path = self.photo.get_photo_path()
        try:
            os.makedirs(os.path.dirname(photo_path), exist_ok=True)
            file: File = await bot.get_file(self.photo.photo_id)
            await bot.download(file=file.file_id, destination=photo_path)
            logger.info(f'Фото успешно скачано: {photo_path}')
        except Exception as e:
            logger.error(f'Ошибка при скачивании файла: {e}')
