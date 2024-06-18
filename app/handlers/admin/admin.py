# import xlsxwriter
import os
from app.database.database import engine, session_maker, Base
from app.database.models.dicts import (
    Mos,
    Filials,
    Zones,
    Violations,
    ProblemBlocs
)
from app.database.models.data import (
    User
)
from sqlalchemy import select
import pandas as pd
from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery, InputFile
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.state import default_state, State, StatesGroup
from app.keyboards.admin import AdminKeyboards
from app.keyboards.default import DefaultKeyboards
from app.handlers.messages import AdminMessages, DefaultMessages
from app.handlers.states import AdminStates
from app.filters.admin import AdminFilter
from loguru import logger
from aiogram.types import FSInputFile


router = Router() 
router.message.filter(AdminFilter())

@router.message(Command('start'))
async def cmd_start(message: Message, state: FSMContext):
    await message.answer(
        text=AdminMessages.start_message,
        reply_markup=AdminKeyboards().main_menu()
    )
    await state.set_state(AdminStates.admin)


@router.message(F.text.lower() == "добавить пользователей",
                StateFilter(AdminStates.admin))
async def add_users_command(message: Message, state: FSMContext, bot:Bot):
    await state.clear()
    await message.answer(
            text=AdminMessages.send_sample,
            # reply_markup=DefaultKeyboards().get_authorization()
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
        doc_title = message.document.file_name
        file = await bot.get_file(doc_id)
        file_path = file.file_path
        if os.path.exists('tmp.xlsx'):
            os.remove('tmp.xlsx')
        await bot.download_file(file_path, 'tmp.xlsx')
        df = pd.read_excel('tmp.xlsx', sheet_name='new', engine='openpyxl')
        df.where(pd.notnull(df), None, inplace=True)

        async with session_maker() as session:
            for _, row in df.iterrows():
                stripped_row = {key: value.strip() if isinstance(value, str) else value for key, value in row.items()}
                logger.info('')
                
                unique_field_value = stripped_row['user_id']
                result = await session.execute(select(User).filter_by(user_id=unique_field_value))
                existing_user = result.scalar()
                
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
            # reply_markup=DefaultKeyboards().get_authorization()
        )
        
    except Exception as e:
        await message.answer(text='Ошибка! Пожалуйста, проверьте отправленные данные (сверьтесь с шаблоном)')
        logger.error(e)

@router.message(F.text.lower() == "посмотреть пользователей",
                StateFilter(AdminStates.admin))
async def export_users_to_excel(message: Message, state: FSMContext, bot:Bot):
    async with session_maker() as session:
        result = await session.execute(select(User))
        users = result.scalars().all()
        
        data = [
            {
                "user_id": user.user_id,
                "mo_": user.mo_,
                "fil_": user.fil_,
                "department": user.department,
                "last_name": user.last_name,
                "first_name": user.first_name,
                "patronymic": user.patronymic,
                "post": user.post,
                "is_admin": user.is_admin,
                "is_mfc": user.is_mfc,
                "is_mfc_leader": user.is_mfc_leader,
                "is_mo_performer": user.is_mo_performer,
                "is_mo_controler": user.is_mo_controler,
                "is_archived": user.is_archived,
                # "created_at": user.created_at,
                # "updated_at": user.updated_at,
            }
            for user in users
        ]
        path_file = 'users.xlsx'

        df = pd.DataFrame(data)
        if os.path.exists(path_file):
            os.remove(path_file)
        users_doc = FSInputFile(path_file)

        df.to_excel(path_file, index=False, engine='xlsxwriter', sheet_name='new')
        await message.answer_document(document=users_doc, caption="Вот ваш файл с данными пользователей.")
        
        os.remove(path_file)


@router.message(F.text.lower() == "назад", StateFilter(AdminStates.admin))
async def back_command(message: Message, state: FSMContext):
    await state.clear()
    user = message.from_user
    await message.answer(
            text=DefaultMessages.start_message,
            reply_markup=DefaultKeyboards().get_authorization()
        )
