import asyncio
import os
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
from aiogram import Bot
from aiogram.client.bot import DefaultBotProperties
from aiogram.types import File
# from openpyxl.drawing.image import Image
from loguru import logger
from sqlalchemy import text

from app.config import settings
from app.database.database import session_maker


# def convert_to_jpeg(file_path):
#     try:
#         with Image.open(file_path) as img:
#             rgb_img = img.convert("RGB")  # Приводим к RGB (некоторые PNG могут быть RGBA)
#             jpeg_path = file_path  # Сохраняем с тем же именем, но в правильном формате
#             rgb_img.save(jpeg_path, format="JPEG", quality=95)
#             return jpeg_path
#     except Exception as e:
#         logger.error(f'Ошибка при конвертации {file_path}: {e}', exc_info=True)
#         return None

@dataclass
class PhotoForSave:
    photo_id: str
    mo: str
    fil: str
    day: str
    zone: str
    problem: str
    violation_name: str
    prefix: str  # mo или mfc в зависимости от того чья фото

    def get_photo_path(self):
        # month = self.day[:6]
        path = os.path.join(
            settings.DATA_PATH,
            # month,
            # self.day,
            # self.mo,
            # self.fil,
            # self.zone,
            # self.violation_name,
            # self.problem,
            # f'{self.prefix}_{self.photo_id}.jpg'
            self.photo_id
        )
        return path


class PhotoSaver:
    def __init__(
            self,
            day: pd.Timestamp,
    ):
        self.day = day

    async def get_photos(self, all_photos=False):
        query = f"""
            select
                photo_id_mo,
                photo_id_mfc,
                mo_,
                c.fil_,
                zone,
                problem,
                violation_name,
                cast(violation_detected as DATE) as violation_detected_day
            from data.violation_found vf
                join dicts.violations v
                on vf.violation_dict_id = v.violation_dict_id
                join data."check" c
                on vf.check_id = c.check_id
                join dicts.filials f
                on c.fil_ = f.fil_
            where cast(violation_detected as DATE) = '{self.day.strftime('%Y-%m-%d')}'
            """

        query_all = """
            select
                photo_id_mo,
                photo_id_mfc,
                mo_,
                c.fil_,
                zone,
                problem,
                violation_name,
                cast(violation_detected as DATE) as violation_detected_day
            from data.violation_found vf
                join dicts.violations v
                on vf.violation_dict_id = v.violation_dict_id
                join data."check" c
                on vf.check_id = c.check_id
                join dicts.filials f
                on c.fil_ = f.fil_
            """

        async with session_maker() as session:
            result = await session.execute(text(query_all if all_photos else query))
            rows = result.fetchall()
            photos = []
            for row in rows:
                if row.photo_id_mo:
                    photos.append(PhotoForSave(
                        photo_id=row.photo_id_mo,
                        mo=row.mo_,
                        fil=row.fil_,
                        day=str(row.violation_detected_day).replace('-', ''),
                        zone=row.zone,
                        problem=row.problem,
                        violation_name=row.violation_name,
                        prefix='mo',
                    ))

                if row.photo_id_mfc:
                    for photo_id_mfc in row.photo_id_mfc:  # т.к. у МФЦ может быть несколько фотографий
                        photos.append(PhotoForSave(
                            photo_id=photo_id_mfc,
                            mo=row.mo_,
                            fil=row.fil_,
                            day=str(row.violation_detected_day).replace('-', ''),
                            zone=row.zone,
                            problem=row.problem,
                            violation_name=row.violation_name,
                            prefix='mfc',
                        ))

            logger.info('get all_photos_day')
            self.photos: list[PhotoForSave] = photos.copy()

    async def download_photos(self, bot: Bot):
        if not self.photos:
            logger.info(f"There is no photos for {self.day.strftime('%Y%m%d')}")
            return
        else:
            for photo in self.photos:
                photo_path = photo.get_photo_path()
                try:
                    os.makedirs(os.path.dirname(photo_path), exist_ok=True)
                    file: File = await bot.get_file(photo.photo_id)
                    file_ext = Path(file.file_path).suffix
                    photo_path_with_ext = f'{photo_path}{file_ext}'
                    await bot.download_file(file_path=file.file_path, destination=photo_path_with_ext)
                    logger.info(f'Фото успешно скачано: {photo_path_with_ext}')
                except Exception as e:
                    logger.error(f'Ошибка при скачивании файла: {e}')

async def scheduler_download_photos():
    report_date = pd.Timestamp('today')
    obj = PhotoSaver(day=report_date)
    await obj.get_photos()
    bot = Bot(token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode='HTML'))
    await obj.download_photos(bot=bot)

async def download_all_photos():
    report_date = pd.Timestamp('today')
    obj = PhotoSaver(day=report_date)
    await obj.get_photos(all_photos=True)
    bot = Bot(token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode='HTML'))
    await obj.download_photos(bot=bot)


if __name__ == '__main__':
    asyncio.run(download_all_photos())
