from aiogram.fsm.state import State, StatesGroup

class MfcStates(StatesGroup):
    start_checking = State()
    choose_time= State()
    choose_zone = State()
    choose_violation = State()
    choose_photo_comm = State()
    add_photo = State()
    add_comm = State()
    continue_state = State()
  

