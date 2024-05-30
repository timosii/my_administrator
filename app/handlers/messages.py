import datetime as dt
from app.utils.utils import time_determiner
from app.view.cards import FormCards


class AdminMessages:
    start_message = 'Привет, админ! Что делать будем'


class DefaultMessages:
    start_message = 'Добрый день! Нажмите кнопку, чтобы я узнал вас!'
    something_wrong = 'Что-то пошло не так. Попробуйте ещё раз или начните сначала /start '
    finish = 'Спасибо, сеанс окончен!'


class MfcMessages:
    start_message = 'Для начала нажмите /start'
    welcome_message = 'Нажмите, чтобы начать проверку'
    choose_fil = f'Вы начали проверку {time_determiner()}. Выберите филиал проверки:'
    choose_zone = 'Выберите зону нарушения:'
    add_photo = 'Отправьте фото'
    add_comm = 'Напишите и отправьте комментарий'
    photo_added = 'Фото добавлено!'
    comm_added = 'Комментарий добавлен!'
    continue_check = 'Вы можете продолжить проверку, либо закончить её, нажав "Закончить проверку"'
    cancel_check = 'Возвращаемся в начало ...'
    finish_check = 'Проверка закончена! Все данные были сохранены. Спасибо за участие!'
    wrong = 'Проверьте, что вы отправляете и попробуйте ещё раз'
    
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
    

class MfcLeaderMessages:
    start_message = "Добро пожаловать, администратор МФЦ!"


class MoPerformerMessages:
    start_message = 'Добро пожаловать, исполнитель МО!'
    choose_fil = 'Выберите филиал:'
    add_photo = 'Отправьте фотографию. Она будет сохранена в качестве фотофиксации исправления нарушения.'
    add_comm = 'Напишите и отправьте текст. Он будет сохранен в качестве комментария к нарушению.'
    photo_added = 'Фото добавлено!'
    comm_added = 'Комментарий добавлен!'
    choose_another = 'Вы можете выбрать другое нарушение из списка нарушений'
    no_violations = 'Для этой проверки нарушений нет!'
    back_to_checks = 'Возвращаемся к списку проверок...'
    continue_check = 'Загружаю нарушения...'
    wrong = 'Проверьте, что вы отправляете и попробуйте ещё раз'
    choose_vio = 'Вы вышли из режима исправления. Выберите нарушение:'

    @staticmethod
    def form_no_checks_answer(fil_: str):
        return f'Активных проверок для филиала {fil_} не найдено'
    
    @staticmethod
    def photo_comm_added(vio_id: int):
        return f'Информация для нарушения добавлена'

    @staticmethod
    def correct_mode(text_mes: str) -> str:
        res = f"Вы в режиме исправления нарушения:\n{text_mes}\nВы можете добавить информацию (написать комментарий и приложить фото)"
        return res

class MoControlerMessages:
    start_message = 'Добро пожаловать, куратор МО!'
