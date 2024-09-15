from app.database.schemas.user_schema import UserBaseInfo


async def get_user_info(user: UserBaseInfo, is_mfc: bool) -> str:
    if is_mfc:
        res = f'''
Фамилия: {user.last_name}
Имя: {user.first_name}
Отчество: {user.patronymic if user.patronymic else 'не указано'}
Отдел: {user.department if user.department else 'не указан'}
Должность: {user.post if user.post else 'не указана'}
'''
    else:
        res = f'''
Фамилия: {user.last_name}
Имя: {user.first_name}
Отчество: {user.patronymic if user.patronymic else 'не указано'}
Должность: {user.post if user.post else 'не указана'}
МО: {user.mo_}
Филиал: {user.fil_}
'''
    return res
