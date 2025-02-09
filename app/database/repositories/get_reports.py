import os

import pandas as pd
from aiogram.types import FSInputFile
from loguru import logger
from sqlalchemy import text

from app.database.database import session_maker


async def get_mfc_report(start_date: str, end_date: str) -> FSInputFile:
    OUT_COLS = {
        # 'check_id': 'ID проверки',
        'check_date': 'Дата проверки',
        # 'mfc_start': 'Начало проверки',
        # 'mfc_finish': 'Окончание проверки',
        'mfc_fio': 'ФИО проверяющего',
        'mfc_post': 'Должность',
        'mo_': 'МО',
        'fil_': 'Филиал',
        'comm_mfc': 'Комментарий МФЦ',
        'zone': 'Зона',
        'violation_name': 'Нарушение',
        'problem': 'Проблематика',
        'comm_mo': 'Комментарий МО',
        'mo_fio': 'ФИО сотрудника МО',
        'mo_post': 'Должность сотрудника МО',
        'violation_detected': 'Время обнаружения нарушения',
        'violation_fixed': 'Время исправления нарушения',
        'violation_pending': 'Время переноса нарушения',
        'pending_period': 'Срок переноса нарушения',
        'is_task': 'В рамках уведомления'
    }
    async with session_maker() as session:
        query = """
        SELECT
            DATE(check_t.mfc_start AT TIME ZONE 'UTC' AT TIME ZONE 'Europe/Moscow') AS check_date,
            CAST(check_t.check_id as varchar) as check_id,
            CAST(violation_found_t.violation_found_id as varchar) as violation_found_id,
            check_t.mfc_start AT TIME ZONE 'UTC' AT TIME ZONE 'Europe/Moscow' AS mfc_start,
            check_t.mfc_finish AT TIME ZONE 'UTC' AT TIME ZONE 'Europe/Moscow' AS mfc_finish,
            mfc_user.last_name || ' ' || mfc_user.first_name || ' ' || COALESCE(mfc_user.patronymic, '') AS MFC_FIO,
            mfc_user.post AS mfc_post,
            fil_t.mo_ AS mo_,
            fil_t.fil_ AS fil_,
            fil_t.fil_population AS fil_population,
            violation_found_t.comm_mfc AS comm_mfc,
            vio_dict_t.zone AS zone,
            vio_dict_t.violation_name AS violation_name,
            vio_dict_t.problem AS problem,
            violation_found_t.comm_mo AS comm_mo,
            mo_user.last_name || ' ' || mo_user.first_name || ' ' || COALESCE(mo_user.patronymic, '') AS MO_FIO,
            mo_user.post AS mo_post,
            violation_found_t.violation_detected AT TIME ZONE 'UTC' AT TIME ZONE 'Europe/Moscow' AS violation_detected,
            violation_found_t.violation_fixed AT TIME ZONE 'UTC' AT TIME ZONE 'Europe/Moscow' AS violation_fixed,
            check_t.is_task AS is_task,
            violation_found_t.is_pending AS is_pending,
            violation_found_t.violation_pending AT TIME ZONE 'UTC' AT TIME ZONE 'Europe/Moscow' AS violation_pending,
            DATE(violation_found_t.pending_period) AS pending_period
        FROM data.check as check_t
        left JOIN data.user AS mfc_user
            ON mfc_user.user_id = check_t.mfc_user_id
        JOIN data.violation_found as violation_found_t
            ON violation_found_t.check_id = check_t.check_id
        left JOIN dicts.filials as fil_t
            ON check_t.fil_ = fil_t.fil_
        left JOIN dicts.violations as vio_dict_t
            ON vio_dict_t.violation_dict_id = violation_found_t.violation_dict_id
        LEFT JOIN data.user AS mo_user
            ON mo_user.user_id = violation_found_t.mo_user_id
        WHERE DATE(check_t.mfc_start AT TIME ZONE 'UTC' AT TIME ZONE 'Europe/Moscow') BETWEEN :start_date AND :end_date
        """
        result = await session.execute(text(query), {'start_date': start_date, 'end_date': end_date})
        rows = result.fetchall()
        if rows:
            df = pd.DataFrame(rows)
            df.columns = result.keys()
            df = df.sort_values(by='check_date')
            df['is_task'] = df['is_task'].map({False: 'Нет', True: 'Да'})
            df = df[OUT_COLS.keys()].rename(columns=OUT_COLS)
        else:
            logger.info('mfc report is empty')
            return None

        logger.info('get mfc report')
        path_file = 'mfc_report.xlsx'
        if os.path.exists(path_file):
            os.remove(path_file)
        mfc_report_doc = FSInputFile(path_file)
        with pd.ExcelWriter(path_file) as writer:
            sheet_name = 'Отчет по нарушениям'
            df.to_excel(writer, index=False, sheet_name=sheet_name)

            worksheet = writer.sheets[sheet_name]

            worksheet.set_column('A:A', 15)
            worksheet.set_column('B:B', 25)
            worksheet.set_column('C:C', 15)
            worksheet.set_column('D:D', 10)
            worksheet.set_column('E:E', 10)
            worksheet.set_column('F:F', 35)
            worksheet.set_column('G:G', 35)
            worksheet.set_column('H:H', 35)
            worksheet.set_column('I:I', 45)
            worksheet.set_column('J:J', 25)
            worksheet.set_column('K:K', 25)
            worksheet.set_column('L:L', 25)
            worksheet.set_column('M:M', 30)
            worksheet.set_column('N:N', 30)
            worksheet.set_column('O:O', 25)
            worksheet.set_column('P:P', 25)
            worksheet.set_column('Q:Q', 25)

        return mfc_report_doc
