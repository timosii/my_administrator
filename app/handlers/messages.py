import datetime as dt
from app.utils.utils import time_determiner, form_greeting
from app.view.cards import FormCards


class AdminMessages:
    start_message = 'Привет, админ! Что делать будем'

class DefaultMessages:
    start_message = f'{form_greeting()}! Нажмите кнопку, чтобы я узнал вас!'
    something_wrong = 'Что-то пошло не так. Попробуйте ещё раз или начните сначала /start '
    not_good_time = 'Сейчас не лучшее время для этого ...'

class MfcMessages:
    start_message = 'Для начала нажмите /start'
    welcome_message = f'{form_greeting()}, исполнитель МФЦ!\nВыберите филиал проверки:'
    main_menu = 'Выберите, что хотите сделать'
    choose_zone_with_time = f'Вы начали проверку {time_determiner()}. Выберите зону нарушения: '
    choose_zone = 'Выберите зону нарушения:'
    add_photo = 'Отправьте фото'
    add_comm = 'Напишите и отправьте комментарий'
    photo_added = 'Фото добавлено!'
    comm_added = 'Комментарий добавлен!'
    continue_check = 'Вы можете продолжить проверку, либо закончить её, нажав "Закончить проверку"'
    cancel_check = 'Возвращаемся в начало ...'
    finish_check = 'Проверка закончена! Все данные были сохранены. Спасибо за участие!'
    wrong = 'Проверьте, что вы отправляете и попробуйте ещё раз'
    check_deleted = 'Проверка успешно удалена!'
    no_unfinished = 'Нет незавершенных проверок'
    violation_already_exist = 'Вы уже зарегистрировали это нарушение. Пожалуйста, выберите другое'
    wrong_state = 'Описание доступно только после выбора нарушения'
    no_description = 'Нет описания'
    notification_add = 'Выберите филиал, где проблема обнаружена'
    problem_detection = 'Вы обнаружили проблему ☑️'
    violation_saved = 'Информация сохранена ✅'

    @staticmethod
    def choose_violation(zone: str) -> str:
        return f'Выберите нарушение в зоне <b>"{zone}"</b>'
    
    @staticmethod
    def add_photo_comm(violation: str) -> str:
        return f'Приложите фото и напишите комментарий по проблеме <b>"{violation}"</b>'

    @staticmethod
    def photo_comm_added(violation: str) -> str:
        message = f'Вы приложили фото и написали комментарий по проблеме <b>"{violation}"</b>.\nСохранить нарушение?'
        return message
    
    @staticmethod
    def save_violation(violation: str) -> str:
        message = f'Мы сохранили нарушение <b>"{violation}"</b>. Спасибо!'
        return message
    
    @staticmethod
    def cancel_violation(violation: str) -> str:
        message = f'Вы можете добавить фото и комментарии для проблемы <b>"{violation}"</b>.'
        return message


    @staticmethod
    def notification_final(mo: str) -> str:
        message = f'Уведомление отправлено в {mo}. Спасибо!'
        return message   
    
class MfcLeaderMessages:
    start_message = f"{form_greeting()}, администратор МФЦ!"

class MoPerformerMessages:
    start_message = f"{form_greeting()}, исполнитель МО! Выберите филиал:"
    choose_fil = 'Выберите филиал:'
    add_photo = 'Отправьте фотографию. Она будет сохранена в качестве фотофиксации исправления нарушения.'
    add_comm = 'Напишите и отправьте текст. Он будет сохранен в качестве комментария к нарушению.'
    photo_added = 'Фото добавлено!'
    comm_added = 'Комментарий добавлен!'
    choose_another = 'Вы можете выбрать другое нарушение из списка нарушений'
    no_violations = 'Для этой проверки нарушений нет!'
    no_violations_buttons = 'Других нарушений нет'
    back_to_checks = 'Возвращаемся к списку проверок...'
    continue_check = 'Загружаю нарушения...'
    wrong = 'Проверьте, что вы отправляете и попробуйте ещё раз'
    choose_vio = 'Вы вышли из режима исправления. Выберите нарушение:'
    cant_finish = 'Вы не можете закончить проверку, остались неисправленные нарушения!'
    can_continue_or_finish = 'Мы всё сохранили. Спасибо!'
    photo_comm_added = 'Информация сохранена ✅'
    choose_check_task = 'Вы можете выбрать активные задачи (это уведомления с нарушениями) или полноценные проверки'
    tasks_work_finish = 'Работа с задачами закончена'

    @staticmethod
    def finish_mes(violation_name: str):
        return f'Вы добавили информацию для нарушения <b>{violation_name}</b>.\nСохранить изменения?'

    @staticmethod
    def form_no_checks_answer(fil_: str):
        return f'Активных проверок для филиала {fil_} не найдено'
    
    @staticmethod
    def form_no_tasks_answer(fil_: str):
        return f'Активных задач для филиала {fil_} нет'

    @staticmethod
    def correct_mode(text_mes: str) -> str:
        res = f"Вы <b>в режиме исправления нарушения</b>:\n{text_mes}\nВы можете добавить информацию (написать комментарий и приложить фото)"
        return res

class MoControlerMessages:
    start_message = f'{form_greeting}, куратор МО!'
