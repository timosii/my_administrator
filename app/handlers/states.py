from aiogram.fsm.state import State, StatesGroup


class MfcStates(StatesGroup):
    choose_mo = State()
    choose_mo_additional = State()
    choose_fil = State()
    choose_type_checking = State()
    choose_zone = State()
    choose_violation = State()
    get_pending = State()
    add_content = State()
    continue_state = State()
    additional_photo = State()


class MfcAvailStates(StatesGroup):
    avail_main = State()
    choose_oms = State()
    get_number = State()
    form_send_mo = State()


class Feedback(StatesGroup):
    feedback = State()


class MoPerformerStates(StatesGroup):
    mo_performer = State()
    pending_period = State()
    pending_process = State()
    take_correct = State()
    correct_violation = State()
    take_save = State()
    save_vio_update = State()


class MoControlerStates(StatesGroup):
    mo_controler = State()


class AdminStates(StatesGroup):
    admin = State()


class RegStates(StatesGroup):
    reg = State()
    get_active = State()
    start_registration = State()
    surname_take = State()
    name_take = State()
    patronymic_take = State()
    post_take = State()

    department_take = State()

    get_mo = State()
    choose_mo_additional = State()
    get_fil = State()
    is_avail_status = State()

    confirmation_reg = State()
    # success_reg = State()


class MfcLeaderStates(StatesGroup):
    mfc_leader = State()
    get_start_period = State()
    get_end_period = State()
    full_period = State()
    finish_stage = State()


class AvailStates(StatesGroup):
    pass
