import os

import pandas as pd
from aiogram.types import FSInputFile
from loguru import logger
from sqlalchemy import text

from app.database.database import session_maker


async def get_mfc_report():
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
        '''
        result = await session.execute(text(query))
        report = result.fetchall()

        data = [
            {
                'check_date': row[0],
                'check_id': row[1],
                'violation_found_id': row[2],
                'mfc_start': row[3],
                'mfc_finish': row[4],
                'mfc_fio': row[5],
                'mfc_post': row[6],
                'mo_': row[7],
                'fil_': row[8],
                'fil_population': row[9],
                'is_mfc_photo': row[10],
                'comm_mfc': row[11],
                'problem': row[12],
                'zone': row[13],
                'violation_name': row[14],
                'comm_mo': row[15],
                'mo_fio': row[16],
                'mo_post': row[17],
                'violation_detected': row[18],
                'violation_fixed': row[19],
                'is_task': row[20],
                'violation_pending': row[21],
            }
            for row in report
        ]
        logger.info('get mfc report')
        path_file = 'mfc_report.xlsx'
        df = pd.DataFrame(data)
        if os.path.exists(path_file):
            os.remove(path_file)
        mfc_report_doc = FSInputFile(path_file)
        df.to_excel(path_file, index=False, engine='xlsxwriter', sheet_name='new')
        return mfc_report_doc
