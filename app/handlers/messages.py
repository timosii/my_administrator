import datetime as dt
from app.utils.utils import time_determiner, form_greeting
from app.view.changelog import CHANGELOG
from app.database.services.users import UserService


class AdminMessages:
    start_message = 'Привет, админ! Что делать будем'
    send_sample = 'Отправляю шаблон, добавьте пользователей по образу и подобию и верните обратно! Если будут ошибки, я сообщу'
    success = 'Вроде всё удачно!'

class DefaultMessages:
    start_message=f'{form_greeting()}! К сожалению не могу узнать вас 👩'
    something_wrong = 'Проверьте введённые данные и попробуйте ещё раз 👌'
    not_good_time = 'Сейчас не лучшее время для этого ...'
    feedback = 'Вы можете отправить сообщение об ошибке или оставить пожелания по улучшениям.\nПоддерживаются <b>фотографии и текст</b>. Как закончите, нажмите <b>"Закончить отправку"</b>.\nСпасибо за участие, вы очень помогаете проекту!'
    feedback_answer = 'Принято! Продолжайте отправлять сообщения или фотографии, а когда закончите нажмите "Закончить отправку"'
    feedback_answer_finish = 'Спасибо, вся информация отправлена разработчикам!\nВы можете продолжить работу с приложением'
    cancel_feedback = 'Возвращаемся обратно! Вы можете продолжить работу с приложением'
    send_changelog = CHANGELOG

class MfcMessages:
    start_message = 'Для начала нажмите /start'
    wrong_type='Чтобы начать, нам нужно определиться с поликлиникой! Введите <b>число</b>'
    main_menu = 'Выберите действие'
    choose_zone_with_time = f'Вы начали проверку {time_determiner()}. Выберите зону нарушения: '
    choose_zone = 'Выберите зону нарушения:'
    add_photo = 'Отправьте фото'
    add_comm = 'Напишите и отправьте комментарий'
    photo_added = 'Фото добавлено!'
    comm_added = 'Комментарий добавлен!'
    continue_check = 'Вы можете продолжить проверку'
    notification_saved = 'Уведомление сохранено!'
    cancel_check = 'Возвращаемся в начало ...'
    finish_check = 'Проверка закончена! Все данные были сохранены. Спасибо за участие!'
    finish_task_zero_violations = 'Создание уведомления отменено, т.к. вы не выбрали ни одного нарушения'
    wrong = 'Проверьте, что вы отправляете и попробуйте ещё раз'
    check_deleted = 'Проверка успешно удалена!'
    no_unfinished = 'Нет незавершенных проверок'
    violation_already_in_check = 'Вы уже зарегистрировали это нарушение. Пожалуйста, выберите другое'
    wrong_state = 'Описание доступно только после выбора нарушения'
    no_description = 'Для этого нарушения нет описания'
    notification_add = 'Выберите филиал, где проблема обнаружена'
    problem_detection = 'Вы обнаружили проблему ☑️'
    violation_saved = 'Информация сохранена ✅'
    does_not_find = 'Мы не нашли вашу поликлинику. Пожалуйста, попробуйте ещё раз или обратитесь к администратору'
    choose_mo_additional='Пожалуйста, выберите MO из предложенных вариантов'
    not_comm_to_photo = 'Вы не добавили комментарий к фотографии. Пожалуйста, повторите'
    need_comm_and_photo = 'Добавьте фотографию и комментарий к нарушению в качестве подписи к фото'
    work_only_with_photo_and_text = 'Поддерживается только фото и текст (в качестве подписи к фото)'
    zero_performers = "Отправка уведомления в МО невозможна: нет зарегистрированных исполнителей в филиале"
    cant_delete = 'Проверка не может быть удалена, есть зарегистрированные нарушения'

    @staticmethod
    async def welcome_message(user_id: int, user_obj: UserService=UserService()) -> str:
        result = f'{form_greeting()}, {await user_obj.get_name(user_id=user_id)}!\nПожалуйста, введите <b>номер</b> поликлиники для проверки:'
        return result
    
    @staticmethod
    def choose_violation(zone: str) -> str:
        return f'Выберите нарушение в зоне <b>"{zone}"</b>'
    
    @staticmethod
    def add_photo_comm(violation_name: str) -> str:
        return f'Приложите фото и напишите комментарий по проблеме <b>"{violation_name}"</b>'

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
    
    @staticmethod
    def choose_fil(mo: str) -> str:
        result = f'Ваша поликлиника: {mo}, пожалуйста выберите филиал проверки'
        return result
    
    @staticmethod
    def violation_sending(fil_: str) -> str:
        result = f"Оповещение о нарушении отправлено сотрудникам {fil_}"
        return result

    @staticmethod
    def there_is_new_violation(fil_: str, text: str) -> str:
        result = f"<b>Зарегистрировано новое нарушение в филиале {fil_}</b>\n{text}"
        return result

    
class MfcLeaderMessages:
    start_message = f"{form_greeting()}, куратор МФЦ!"

class MoPerformerMessages:
    choose_fil = 'Выберите филиал:'
    add_photo = 'Отправьте фотографию. Она будет сохранена в качестве фотофиксации исправления нарушения.'
    add_comm = 'Напишите и отправьте текст. Он будет сохранен в качестве комментария к нарушению.'
    photo_added = 'Фото добавлено!'
    comm_added = 'Комментарий добавлен!'
    choose_another = 'Вы можете выбрать другое нарушение из списка нарушений'
    no_violations = 'Для этой проверки активных нарушений нет!'
    no_violations_buttons = 'Больше нарушений нет'
    back_to_checks = 'Возвращаемся к списку проверок...'
    continue_check = 'Загружаю нарушения...'
    wrong = 'Проверьте, что вы отправляете и попробуйте ещё раз'
    choose_vio = 'Вы вышли из режима исправления. Выберите нарушение:'
    cant_finish = 'Вы не можете закончить проверку, остались неисправленные нарушения!'
    can_continue_or_finish = 'Мы всё сохранили. Спасибо!'
    photo_comm_added = 'Информация сохранена ✅'
    choose_check_task = 'Вы можете выбрать активные уведомления, активные проверки или перенесенные нарушения'
    tasks_work_finish = 'Работа с уведомлением закончена. Спасибо!'
    exit_first = 'Сначала выйдете из режима исправления'
    exit_take = 'Вы вышли из режима исправления нарушения'
    move_to_pending_alert = 'Нарушение будет находиться в статусе "Перенесено" и не отображаться среди других нарушений.\nВы сможете найти такие нарушения в пункте "Перенесенные нарушения" главного меню'
    move_to_pending = 'Нарушение перенесено. Вы можете продолжить работу'
    finish_check_zero_violations = 'Проверка завершена без активных нарушений!'
    violation_already_fixed = "Нарушение уже исправлено"

    @staticmethod
    async def welcome_message(user_id: int, user_obj: UserService=UserService()) -> str:
        result = f'{form_greeting()}, {await user_obj.get_name(user_id=user_id)}!\nВы можете выбрать активные уведомления, активные проверки или перенесенные нарушения'
        return result
    
    @staticmethod
    def finish_mes(violation_name: str):
        return f'Вы добавили информацию для нарушения <b>{violation_name}</b>.\nСохранить изменения?'

    @staticmethod
    def form_no_checks_answer(fil_: str):
        return f'Активных проверок для филиала {fil_} не найдено'
    
    @staticmethod
    def form_no_tasks_answer(fil_: str):
        return f'Активных уведомлений для филиала {fil_} нет'
    
    @staticmethod
    def form_no_pending_violations_answer(fil_: str):
        return f'Перенесенных нарушений для филиала {fil_} нет'

    @staticmethod
    def correct_mode(text_mes: str) -> str:
        res = f"Вы <b>в режиме исправления нарушения</b>:\n{text_mes}\nПожалуйста, приложите фотографию и добавьте комментарий в качестве подписи"
        return res

class MoControlerMessages:
    start_message = f'{form_greeting}, куратор МО!'
