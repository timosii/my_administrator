from aiogram.fsm.state import State, StatesGroup


class MfcStates(StatesGroup):
    choose_mo=State()
    choose_mo_additional=State()
    choose_fil= State()
    choose_type_checking = State()
    choose_zone = State()
    choose_violation = State()
    get_pending = State()
    add_content = State()
    continue_state = State()
  
class Feedback(StatesGroup):
    feedback = State()

class MoPerformerStates(StatesGroup):
    mo_performer = State()
    correct_violation = State()
    save_vio_update = State()

class MoControlerStates(StatesGroup):
    mo_controler = State()


class AdminStates(StatesGroup):
    admin = State()


class MfcLeaderStates(StatesGroup):
    mfc_leader = State()
