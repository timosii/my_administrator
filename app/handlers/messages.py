from app.utils.utils import time_determiner
from app.data import ZONES

class Messages:
    def __init__(self) -> None:
        self.zone = None
        self.violation = None

    @staticmethod
    def main_menu() -> str:
        welcome_message = 'Нажмите, чтобы начать проверку'
        return welcome_message

    @staticmethod
    def get_welcome_message() -> str:
        start_message = f'{time_determiner()}.Выберите время проверки:'
        return start_message
    
    @staticmethod
    def choose_zone() -> str:
        return 'Выберите зону нарушения:'
    
    def choose_violation(self) -> str:
        return f'Выберите нарушение в зоне {self.zone}'
    
    def add_photo_comm(self) -> str:
        return f'Приложите фото и напишите комментарий по проблеме {self.violation}'
    
    @staticmethod
    def add_photo() -> str:
        return 'Отправьте фото'
    
    @staticmethod
    def add_comm() -> str:
        return 'Напишите и отправьте комментарий'
    
    def photo_comm_added(self) -> str:
        message = f'Вы приложили фото и написали комментарий по проблеме {self.violation}, вернуться к зоне нарушения {self.zone} или к выбору зон нарушений?'
        return message


