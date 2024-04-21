from app.utils.utils import time_determiner
from app.data import ZONES

class Messages:
    def __init__(self) -> None:
        self.zone = None
        self.violation = None

    @staticmethod
    def get_welcome_message() -> str:
        welcome_message = f'{time_determiner()}.Выберите время проверки:'
        return welcome_message
    
    @staticmethod
    def choose_zone() -> str:
        return 'Выберите зону нарушения:'
    
    def choose_violation(self) -> str:
        return f'Выберите нарушение в зоне {self.zone}'
    
    def add_photo_comm(self) -> str:
        return f'Приложите фото и напишите комментарий по проблеме {self.violation}'
    
    def photo_comm_added(self) -> str:
        message = f'Вы приложили фото и написали комментарий по проблеме {self.violation}, вернуться к зоне нарушения {self.zone} или к выбору зон нарушений?'
        return message


