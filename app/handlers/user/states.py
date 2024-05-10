from aiogram.fsm.state import State, StatesGroup

class MfcStates(StatesGroup):
    choose_time= State()
    choose_zone = State()
    choose_violation = State()
    choose_photo_comm = State()
    add_photo = State()
    add_comm = State()
    continue_state = State()
    # add_photo_after_comm = State()
    # add_comm_after_photo = State()
    

