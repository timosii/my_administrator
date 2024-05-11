from app.utils.utils import time_determiner
from app.data import ZONES

class Messages:

    @staticmethod
    def start_message() -> str:
        return 'Для начала нажмите /start'
    
    @staticmethod
    def main_menu() -> str:
        welcome_message = 'Нажмите, чтобы начать проверку'
        return welcome_message

    @staticmethod
    def choose_time() -> str:
        start_message = f'{time_determiner()}. Выберите время проверки:'
        return start_message
    
    @staticmethod
    def choose_zone() -> str:
        return 'Выберите зону нарушения:'
    
    @staticmethod
    def choose_violation(zone: str) -> str:
        return f'Выберите нарушение в зоне {zone}'
    
    @staticmethod
    def add_photo_comm(violation: str) -> str:
        return f'Приложите фото и напишите комментарий по проблеме {violation}'
    
    @staticmethod
    def add_photo() -> str:
        return 'Отправьте фото'
    
    @staticmethod
    def add_comm() -> str:
        return 'Напишите и отправьте комментарий'
    
    @staticmethod
    def photo_added() -> str:
        return 'Фото добавлено!'
    
    @staticmethod
    def comm_added() -> str:
        return 'Комментарий добавлен!'
    
    @staticmethod
    def photo_comm_added(zone: str, violation: str) -> str:
        message = f'Вы приложили фото и написали комментарий по проблеме <b>{violation}</b>. Сохранить нарушение?'
        return message


