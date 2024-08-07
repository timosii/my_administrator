import os

import pandas as pd
from aiogram.types import FSInputFile
from loguru import logger
from sqlalchemy import text

from app.database.database import session_maker


async def get_mfc_report(start_date: str, end_date: str) -> FSInputFile:
    OUT_COLS = {
        'check_id': 'ID проверки',
        'check_date': 'Дата проверки',
        # 'mfc_start': 'Начало проверки',
        # 'mfc_finish': 'Окончание проверки',
        'mfc_fio': 'ФИО проверяющего',
        'mfc_post': 'Должность',
        'mo_': 'МО',
        'fil_': 'Филиал',
        'comm_mfc': 'Комментарий МФЦ',
        'problem': 'Проблематика',
        'zone': 'Зона',
        'violation_name': 'Нарушение',
        'comm_mo': 'Комментарий МО',
        'mo_fio': 'ФИО сотрудника МО',
        'mo_post': 'Должность сотрудника МО',
        'violation_detected': 'Время обнаружения нарушения',
        'violation_fixed': 'Время исправления нарушения',
        'violation_pending': 'Время переноса нарушения',
        'is_task': 'Уведомление'
    }
    async with session_maker() as session:
        query = '''
        SELECT
            DATE(data."check".mfc_start AT TIME ZONE 'UTC' AT TIME ZONE 'Europe/Moscow') AS check_date,
            data."check".check_id,
            data.violation_found.violation_found_id,
            data."check".mfc_start AT TIME ZONE 'UTC' AT TIME ZONE 'Europe/Moscow' AS mfc_start,
            data."check".mfc_finish AT TIME ZONE 'UTC' AT TIME ZONE 'Europe/Moscow' AS mfc_finish,
            mfc_user.last_name || ' ' || mfc_user.first_name || ' ' || COALESCE(mfc_user.patronymic, '') AS MFC_FIO,
            mfc_user.post AS mfc_post,
            dicts.filials.mo_,
            dicts.filials.fil_,
            dicts.filials.fil_population,
            CASE
                WHEN data.violation_found.photo_id_mfc IS NOT NULL THEN TRUE
                ELSE FALSE
            END AS is_mfc_photo,
            data.violation_found.comm_mfc,
            dicts.violations.problem,
            dicts.violations.zone,
            dicts.violations.violation_name,
            dicts.violations.description,
            data.violation_found.comm_mo,
            mo_user.last_name || ' ' || mo_user.first_name || ' ' || COALESCE(mo_user.patronymic, '') AS MO_FIO,
            mo_user.post AS mo_post,
            data.violation_found.violation_detected AT TIME ZONE 'UTC' AT TIME ZONE 'Europe/Moscow' AS violation_detected,
            data.violation_found.violation_fixed AT TIME ZONE 'UTC' AT TIME ZONE 'Europe/Moscow' AS violation_fixed,
            data."check".is_task,
            data.violation_found.violation_pending AT TIME ZONE 'UTC' AT TIME ZONE 'Europe/Moscow' AS violation_pending
        FROM data."check"
        JOIN data."user" AS mfc_user
            ON mfc_user.user_id = data."check".mfc_user_id
        JOIN data.violation_found
            ON data.violation_found.check_id = data."check".check_id
        JOIN dicts.filials
            ON data."check".fil_ = dicts.filials.fil_
        JOIN dicts.violations
            ON dicts.violations.violation_dict_id = data.violation_found.violation_dict_id
        LEFT JOIN data."user" AS mo_user
            ON mo_user.user_id = data.violation_found.mo_user_id
        WHERE DATE(data."check".mfc_start AT TIME ZONE 'UTC' AT TIME ZONE 'Europe/Moscow') BETWEEN :start_date AND :end_date
        '''
        result = await session.execute(text(query), {'start_date': start_date, 'end_date': end_date})
        rows = result.fetchall()
        if rows:
            df = pd.DataFrame(rows)
            df.columns = result.keys()
            df = df.sort_values(by='check_id')
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
            worksheet.set_column('B:B', 15)
            worksheet.set_column('C:C', 25)
            worksheet.set_column('D:D', 15)
            worksheet.set_column('E:E', 10)
            worksheet.set_column('F:F', 10)
            worksheet.set_column('G:G', 35)
            worksheet.set_column('H:H', 35)
            worksheet.set_column('I:I', 35)
            worksheet.set_column('J:J', 45)
            worksheet.set_column('K:K', 25)
            worksheet.set_column('L:L', 25)
            worksheet.set_column('M:M', 25)
            worksheet.set_column('N:N', 30)
            worksheet.set_column('O:O', 30)
            worksheet.set_column('P:P', 30)
            worksheet.set_column('Q:Q', 15)
            

        return mfc_report_doc
