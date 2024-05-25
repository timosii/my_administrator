from app.utils.utils import time_determiner


class AdminMessages:
    start_message = 'Привет, админ! Что делать будем'


class DefaultMessages:
    start_message = 'Добрый день! Нажмите кнопку, чтобы я узнал вас!'


class MfcMessages:
    start_message = 'Для начала нажмите /start'
    welcome_message = 'Нажмите, чтобы начать проверку'
    choose_fil = f'Вы начали проверку {time_determiner()}. Выберите филиал проверки:'
    choose_zone = 'Выберите зону нарушения:'
    add_photo = 'Отправьте фото'
    add_comm = 'Напишите и отправьте комментарий'
    photo_added = 'Фото добавлено!'
    comm_added = 'Комментарий добавлен!'
    continue_check = 'Вы можете продолжить проверку'
    cancel_check = 'Возвращаемся в начало ...'
    finish_check = 'Проверка закончена! Все данные были сохранены. Спасибо за участие!'
    
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


class MoControlerMessages:
    start_message = 'Добро пожаловать, куратор МО!'
