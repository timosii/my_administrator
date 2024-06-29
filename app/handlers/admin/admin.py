# import xlsxwriter
import os

import numpy as np
import pandas as pd
from aiogram import Bot, F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile, Message
from loguru import logger
from sqlalchemy import select

from app.database.database import session_maker
from app.database.models.data import User
from app.filters.admin import AdminFilter
from app.handlers.messages import AdminMessages, DefaultMessages
from app.handlers.states import AdminStates
from app.keyboards.admin import AdminKeyboards

router = Router()
router.message.filter(AdminFilter())


@router.message(Command('start'))
async def cmd_start(message: Message, state: FSMContext):
    await message.answer(
        text=AdminMessages.start_message,
        reply_markup=AdminKeyboards().main_menu()
    )
    await state.set_state(AdminStates.admin)


@router.message(F.text.lower() == 'добавить пользователей',
                StateFilter(AdminStates.admin))
async def add_users_command(message: Message, state: FSMContext, bot: Bot):
    await state.clear()
    await message.answer(
        text=AdminMessages.send_sample,
    )
    users_sample_path = 'app/database/insert_dicts/data/users_insert.xlsx'
    users_sample_doc = FSInputFile(users_sample_path)
    await message.answer_document(
        document=users_sample_doc,
    )
    await state.set_state(AdminStates.admin)


@router.message(F.content_type == 'document',
                StateFilter(AdminStates.admin))
async def process_doc_command(
        message: Message,
        bot: Bot):
    try:
        doc_id = message.document.file_id
        logger.info(f'DOC_ID: {doc_id}')
        file = await bot.get_file(doc_id)
        file_path = file.file_path
        if os.path.exists('tmp.xlsx'):
            os.remove('tmp.xlsx')
        await bot.download_file(file_path, 'tmp.xlsx')
        df = pd.read_excel('tmp.xlsx', sheet_name='new', engine='openpyxl')
        df = df.replace(np.nan, None)

        async with session_maker() as session:
            for _, row in df.iterrows():
                stripped_row = {key: value.strip() if isinstance(value, str) else value for key, value in row.items()}

                unique_field_value = stripped_row['user_id']
                result = await session.execute(select(User).filter_by(user_id=unique_field_value))
                existing_user = result.scalar()
                if unique_field_value is None:
                    logger.error(f'Missing user_id in row: {stripped_row}')
                    continue

                if existing_user:
                    updated = False
                    for key, value in stripped_row.items():
                        if getattr(existing_user, key) != value:
                            setattr(existing_user, key, value)
                            updated = True

                    if updated:
                        session.add(existing_user)
                else:
                    new_user = User(**stripped_row)
                    session.add(new_user)
            await session.commit()
        await message.answer(
            text=AdminMessages.success,
        )

    except Exception as e:
        await message.answer(text='Ошибка! Пожалуйста, проверьте отправленные данные (сверьтесь с шаблоном)')
        logger.error(e)


@router.message(F.text.lower() == 'посмотреть пользователей',
                StateFilter(AdminStates.admin))
async def export_users_to_excel(message: Message, state: FSMContext, bot: Bot):
    async with session_maker() as session:
        result = await session.execute(select(User))
        users = result.scalars().all()

        data = [
            {
                'user_id': user.user_id,
                'mo_': user.mo_,
                'fil_': user.fil_,
                'department': user.department,
                'last_name': user.last_name,
                'first_name': user.first_name,
                'patronymic': user.patronymic,
                'post': user.post,
                'is_admin': user.is_admin,
                'is_mfc': user.is_mfc,
                'is_mfc_leader': user.is_mfc_leader,
                'is_mo_performer': user.is_mo_performer,
                'is_mo_controler': user.is_mo_controler,
                'is_archived': user.is_archived,
            }
            for user in users
        ]
        path_file = 'users.xlsx'

        df = pd.DataFrame(data)
        if os.path.exists(path_file):
            os.remove(path_file)
        users_doc = FSInputFile(path_file)

        df.to_excel(path_file, index=False, engine='xlsxwriter', sheet_name='new')
        await message.answer_document(document=users_doc, caption='Вот ваш файл с данными пользователей.')

        os.remove(path_file)


@router.message(F.text.lower() == 'назад', StateFilter(AdminStates.admin))
async def back_command(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        text=DefaultMessages.start_message,
        reply_markup=AdminKeyboards().main_menu()
    )
