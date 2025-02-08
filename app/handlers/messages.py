import datetime as dt

from app.database.services.users import UserService
from app.utils.utils import define_word, ending_define, form_greeting
from app.view.changelog import CHANGELOG


class AdminMessages:
    start_message = 'Привет, админ! Что делать будем'
    send_sample = 'Отправляю шаблон, добавьте пользователей и верните обратно. Если будут ошибки, я сообщу'
    success = 'Вроде всё удачно!'


class AuthorizationMessages:
    start_message = 'Здравствуйте! Кажется вы не зарегистрированы. Пожалуйста введите пароль для регистрации'
    archieved_mes = 'Здравствуйте! Ваш аккаунт неактивен. Если хотите активировать его, введите пароль для регистрации'
    incorrect_pass = 'Пароль неверный! Обратитесь к администратору или заново нажмите /start, если ошиблись'
    are_you_sure = 'Вы будете зарегистрированы как {category}\nПродолжить?'
    press_start = 'Для начала нажмите /start'
    anketa = 'Сейчас я попрошу вас ответить на несколько вопросов. Если есть кнопка <b>"Пропустить"</b>, значит на вопрос можно не отвечать\nЭто займет не больше минуты'

    get_surname = 'Введите фамилию:'
    get_name = 'Введите имя:'
    # МО и филиал обязательно для МО
    get_mo = 'Введите номер МО:'
    get_fil = 'Выберите филиал:'
    # опционально
    get_patronymic = 'Введите отчество:'
    get_post = 'Введите должность:'
    get_department = 'Введите номер отдела:'

    is_avail = 'Участвуете ли вы в проекте "Доступность у инфомата"?'

    control_data = 'Все данные получены, пожалуйста, проверьте их:'

    @staticmethod
    async def welcome_message(user_id: int,
                              category: str,
                              user_obj: UserService = UserService()) -> str:
        result = f'Спасибо за регистрацию, {await user_obj.get_name(user_id=user_id)}!\nВы зарегистрированы как {category}\nНажмите /start для начала работы'
        return result


class ErrorMessages:
    network_error = 'Проблема соединения с сервером Телеграм, подождите пару секунд и попробуйте ещё раз 👌'
    server_error = 'Проблема с серверами Телеграм, подождите пару секунд и попробуйте ещё раз 👌'
    bad_request = 'К сожалению, Телеграм не может обработать эту команду 😵'
    tg_error = 'Ошибка со стороны Телеграм. Подождите несколько секунд и попробуйте ещё раз 👌'
    attribute_error_process = 'Объекта, к которому вы обращаетесь, больше не существует, или он существенно изменен 😲. Попробуйте начать с меню 👌'
    process_error = 'Хм, что-то неожиданное! Проверьте введенные данные и попробуйте ещё раз 👌\nЕсли ничего не помогает, сообщите нам об ошибке 👀'


class DefaultMessages:
    vacation = 'Хорошего отдыха! ☀️🌴🌊'
    start_message = f'{form_greeting()}! К сожалению не могу узнать вас 👩'
    something_wrong = 'Проверьте введённые данные и попробуйте ещё раз 👌'
    does_not_find = 'Мы не нашли вашу поликлинику. Пожалуйста, попробуйте ещё раз или обратитесь к администратору'

    choose_mo_additional = 'Пожалуйста, выберите MO из предложенных вариантов'

    not_good_time = 'Сейчас не лучшее время для этого ...'
    feedback = 'Вы можете отправить сообщение об ошибке или оставить пожелания по улучшениям.\nПоддерживаются <b>фотографии и текст</b>. Как закончите, нажмите <b>"Закончить отправку"</b>.\nСпасибо за участие, вы очень помогаете проекту!'
    feedback_answer = 'Принято! Продолжайте отправлять сообщения или фотографии, а когда закончите нажмите "Закончить отправку"'
    feedback_answer_finish = 'Спасибо, вся информация отправлена разработчикам!\nВы можете продолжить работу с приложением'
    cancel_feedback = 'Возвращаемся обратно! Вы можете продолжить работу с приложением'
    send_changelog = CHANGELOG
    back_to_menu = 'Возвращаемся в меню'

    @staticmethod
    def choose_fil(mo: str) -> str:
        result = f'Ваша поликлиника: {mo}, пожалуйста выберите филиал'
        return result

    @staticmethod
    def complete_fil(fil: str) -> str:
        result = f'Ваш филиал: {fil}'
        return result


class MfcMessages:
    start_message = 'Для начала нажмите /start'
    wrong_type = 'Чтобы начать, нам нужно определиться с поликлиникой! Введите <b>число</b>'
    please_start = 'Пожалуйста, начните заново (команда /start)'
    main_menu = 'Пожалуйста, выберите действие:\n\n<b>Начать проверку</b>:\nВы начнёте обычную проверку, все нарушения будут сохранены и отправлены в МО. В день проводится одна проверка, во время которой вы фиксируете все нарушения. После окончания проверки нажмите кнопку <b>"Закончить проверку"</b> в меню выбора зоны.\n\n<b>Проверить незавершенные проверки</b>:\nЗдесь будут проверки, которые вы не закончили. Воспользуйтесь этим пунктом, если вы нажали <b>start</b> во время проверки или произошла техническая неполадка. В остальных случаях вы всегда можете продолжить проверку на том месте, где остановились.\n\n<b>Добавить уведомление о нарушении</b>:\nВы можете отправить уведомление о нарушении в МО, если вне проверки вы обнаружили нарушение и о нём нужно срочно сообщить.\n\n<b>Доступность у инфомата</b>:\nСообщить в МО о невозможности записи у инфомата.'
    choose_zone_with_time = 'Вы начали новую проверку. Выберите зону нарушения: '
    choose_zone_with_time_task = 'Вы создали новое уведомление. Выберите зону нарушения: '
    choose_zone = 'Выберите зону нарушения:'
    add_photo = 'Отправьте фото'
    add_comm = 'Напишите и отправьте комментарий'
    photo_added = 'Фото добавлено!'
    comm_added = 'Комментарий добавлен!'
    continue_check = 'Вы можете продолжить проверку'
    notification_saved = 'Уведомление сохранено!'
    cancel_check = 'Возвращаемся в меню'
    finish_check = 'Проверка закончена! Все данные были сохранены. Спасибо!👌\n\nКстати, вы всегда можете проверить наличие <b>незавершенных проверок</b>: пункт меню <b>Проверить незавершенные проверки</b>\n\nЕсли вы когда-то начинали проверку, но не закончили её, вы сможете её закончить. А если там нет нарушений, то просто удалить! 😉'
    finish_task_zero_violations = 'Создание уведомления отменено, т.к. вы не выбрали ни одного нарушения'
    wrong = 'Проверьте, что вы отправляете и попробуйте ещё раз'
    check_deleted = 'Проверка успешно удалена!'
    no_unfinished = 'Нет незавершенных проверок ✅'
    violation_already_in_check = 'Вы уже зарегистрировали это нарушение. Пожалуйста, выберите другое'
    wrong_state = 'Описание доступно только после выбора нарушения'
    # no_description = 'Для этого нарушения нет описания'
    notification_add = 'Выберите филиал, где проблема обнаружена'
    problem_detection = 'Вы обнаружили проблему ☑️'
    violation_saved = 'Информация сохранена ✅'
    cant_add_photo = 'Вы больше не можете добавлять фото (максимум 10 шт)'

    not_comm_to_photo = 'Вы не добавили комментарий к фотографии. Пожалуйста, повторите'
    need_comm_and_photo = 'Добавьте фотографию и комментарий к нарушению в качестве подписи к фото'
    work_only_with_photo_and_text = 'Поддерживается только фото и текст (в качестве подписи к фото)'
    zero_performers = 'Отправка уведомления в МО невозможна: нет зарегистрированных исполнителей в филиале'
    cant_delete = 'Проверка не может быть удалена, есть зарегистрированные нарушения'
    save_sticker = 'CAACAgEAAxkBAAEGSyRmdAuwBUQuDe3UOYfTRab8RpLFzQACCAIAAoCN0UbbYuEuHFi7_DUE'
    no_violations = 'Больше нарушений нет'
    add_violation_whatever = 'Это нарушение ранее <b>уже было зарегистрировано и перенесено сотрудником МО</b>\nНиже вы можете ознакомиться с деталями. Если хотите добавить <b><u>новое нарушение</u></b>, нажмите <b>"Добавить новое нарушение"</b>'
    watch_sticker = 'CAACAgEAAxkBAAEGSuBmdAVl03axNZqRKohxhbiwzs1D6AACgAIAAqFjGUSrWD-iBcJN3DUE'
    there_is_new_ud = 'Зафиксирована <b>невозможность записи</b> у инфомата:\n'

    @staticmethod
    async def welcome_message(user_id: int, user_obj: UserService = UserService()) -> str:
        result = f'{form_greeting()}, {await user_obj.get_name(user_id=user_id)}!\nПожалуйста, введите <b>номер</b> поликлиники для проверки.\nЕсли у поликлиники нет номера, введите название, например <b>Кузнечики</b>:'
        return result

    @staticmethod
    async def choose_violation(zone: str) -> str:
        return f'Выберите нарушение в зоне <b>"{zone}"</b>'

    @staticmethod
    async def choose_problem(violation_name: str, zone: str) -> str:
        return f'Выберите проблему для нарушения <b>"{violation_name}"</b> в зоне <b>"{zone}"</b>'

    @staticmethod
    async def add_photo_comm(
            zone: str,
            violation_name: str,
            problem: str) -> str:
        return f'Приложите фото и напишите комментарий по проблеме <b>"{problem}"</b> нарушения <b>"{violation_name}"</b> в категории <b>"{zone}"</b>'

    @staticmethod
    async def photo_comm_added(
            zone: str,
            violation_name: str,
            problem: str) -> str:
        message = f'Вы приложили фото и написали комментарий по проблеме <b>"{problem}"</b> нарушения <b>"{violation_name}"</b> в категории <b>"{zone}"</b>.\nСохранить нарушение?'
        return message

    @staticmethod
    async def photo_additional_added(
            zone: str,
            violation_name: str,
            problem: str) -> str:
        message = f'Дополнительные фото по проблеме <b>"{problem}"</b> нарушения <b>"{violation_name}"</b> в категории <b>"{zone}"</b> добавлены.\nСохранить нарушение?'
        return message

    @staticmethod
    async def photo_additional(
            zone: str,
            violation_name: str,
            problem: str) -> str:
        message = f'Отправляйте дополнительные фотографии по проблеме <b>"{problem}"</b> нарушения <b>"{violation_name}"</b> в категории <b>"{zone}"</b>.\nКогда закончите — нажмите кнопку'
        return message

    @staticmethod
    async def save_violation(
            zone: str,
            violation_name: str,
            problem: str) -> str:
        message = f'Мы сохранили нарушение <b>"{violation_name}"</b> по проблеме <b>"{problem}"</b> в категории <b>"{zone}"</b>. Спасибо!'
        return message

    @staticmethod
    async def cancel_violation(
            zone: str,
            violation_name: str,
            problem: str) -> str:
        message = f'Вы можете добавить фото и комментарии для проблемы <b>"{problem}"</b> нарушения <b>"{violation_name}"</b> в категории <b>"{zone}"</b>.'
        return message

    @staticmethod
    async def notification_final(mo: str) -> str:
        message = f'Уведомление отправлено в {mo}. Спасибо!'
        return message

    @staticmethod
    async def violation_sending(fil_: str, count: int, flag: bool) -> str:
        if flag:
            result = f'Оповещение в телеграм <b>отправлено</b> {count} сотрудник{ending_define(count)} филиала {fil_}.'
        else:
            result = f'Оповещение <b>не удалось отправить</b> {count} сотрудник{ending_define(count)} филиала {fil_}.\nДля получения оповещений {define_word(count)} необходимо познакомиться с сервисом 🤝'
        return result

    @staticmethod
    async def there_is_new_violation(fil_: str, text: str) -> str:
        result = f'<b>Зарегистрировано новое нарушение в филиале {fil_}</b>\n{text}'
        return result

    @staticmethod
    async def send_to_mo(fil_: str):
        result = f'Отправляю нарушение сотрудникам {fil_} ...'
        return result


class MfcLeaderMessages:
    start_message = f'{form_greeting()}, куратор МФЦ!'
    choose_period = 'Выберите начало периода: '


class MoPerformerMessages:
    choose_fil = 'Выберите филиал:'
    add_photo = 'Отправьте фотографию. Она будет сохранена в качестве фотофиксации исправления нарушения.'
    add_comm_pending = 'Напишите и отправьте <b>текст</b>. Он будет сохранен в качестве комментария к переносу нарушения.'
    photo_added = 'Фото добавлено!'
    comm_added = 'Комментарий добавлен!'
    choose_another = 'Вы можете выбрать другое нарушение из списка нарушений'
    no_violations = 'Для этой проверки активных нарушений нет 🔥\nНе забудьте закончить проверку (кнопка в меню <b>Закончить проверку</b>) 😉'
    no_violations_buttons = 'Больше нарушений нет'
    no_violations_after_pending = 'Больше нарушений нет.\nПожалуйста, убедитесь, что для филиала нет <b>активных проверок</b> ✅'
    no_violations_in_tasks = 'Больше уведомлений нет.\nПожалуйста, убедитесь, что для филиала нет <b>активных проверок</b> ✅'
    back_to_checks = 'Возвращаемся к списку проверок...'
    find_sticker = 'CAACAgEAAxkBAAEGSuZmdAWRe57jsx-P0BhfRfCxOQagvgACRgMAAiqHGURoXzCXdu7QsTUE'
    technic_sticker = 'CAACAgEAAxkBAAEGSupmdAWynChQQsSPGf7Iy6vadr3S-AACMQIAAsOjKEdLBVdiYsQQXzUE'
    send_sticker = 'CAACAgEAAxkBAAEGSuJmdAV0CQfWJxBE-WC0KiENXGFoGAACBwUAArgvIUS1HNBHhQnpPjUE'
    top_sticker = 'CAACAgEAAxkBAAEGSvhmdAZZ0WnNe6NdE8eZw9sCMxmS9AACVAIAAnPDMURXjXgfqUkMFjUE'
    watch_sticker = 'CAACAgEAAxkBAAEGSuBmdAVl03axNZqRKohxhbiwzs1D6AACgAIAAqFjGUSrWD-iBcJN3DUE'
    save_sticker = 'CAACAgEAAxkBAAEGSyRmdAuwBUQuDe3UOYfTRab8RpLFzQACCAIAAoCN0UbbYuEuHFi7_DUE'
    choose_pending_period = 'Выберите <b>срок переноса:</b>'
    add_pending_comm = 'Добавьте комментарий для переноса нарушения.\nВ нём вы можете указать <b>причину переноса</b>'
    continue_check = 'Загружаю нарушения...'
    wrong = 'Проверьте, что вы отправляете и попробуйте ещё раз'
    choose_vio = 'Вы вышли из режима исправления. Выберите нарушение:'
    cant_finish = 'Вы не можете закончить проверку, остались активные нарушения'
    can_continue_or_finish = 'Мы всё сохранили. Спасибо! 👌'
    photo_comm_added = 'Информация сохранена ✅'
    choose_check_task = 'Вы можете выбрать активные уведомления, активные проверки или перенесенные нарушения'
    tasks_work_finish = 'Работа с уведомлениями закончена. Спасибо! 🔥'
    exit_first = 'Сначала выйдете из режима исправления (кнопка "Отменить" под карточкой нарушения)'
    exit_take = 'Вы вышли из режима исправления нарушения'
    exit_take_save = 'Мы отменили сохранение нарушения ✅'
    move_to_pending_alert = 'Нарушение будет находиться в статусе "Перенесено" и не отображаться среди других нарушений.\nВы сможете найти такие нарушения в пункте "Перенесенные нарушения" главного меню'
    move_to_pending = 'Нарушение перенесено. Вы можете продолжить работу'
    finish_check_zero_violations = 'Проверка завершена!👌'
    violation_already_fixed = 'Нарушение уже исправлено'
    no_photo_added = 'Вы не добавили комментарий к фотографии. Пожалуйста, повторите'
    only_photo_text = 'Поддерживается только фото и текст (в качестве подписи к фото)'
    no_pending = 'Перенесенных нарушений нет 👌'
    can_continue_pending = 'Вы можете продолжить работу с перенесенными нарушениями'
    can_continue_check = 'Вы можете продолжить проверку или закончить её (доступно, если нет активных нарушений)'
    pending_continue = 'Нарушение сохранено в статусе <b>перенесено</b>.\nВозвращаемся к списку нарушений ...'

    @staticmethod
    async def welcome_message(user_id: int, user_obj: UserService = UserService()) -> str:
        result = f'{form_greeting()}, {await user_obj.get_name(user_id=user_id)}!\nВы можете выбрать активные уведомления, активные проверки или перенесенные нарушения'
        return result

    @staticmethod
    async def finish_mes(violation_name: str):
        return f'Вы добавили информацию для нарушения <b>{violation_name}</b>.\nСохранить изменения?'

    @staticmethod
    async def form_no_checks_answer(fil_: str):
        return f'Активных проверок для филиала {fil_} нет'

    @staticmethod
    async def form_no_tasks_answer(fil_: str):
        return f'Активных уведомлений для филиала {fil_} нет'

    @staticmethod
    async def form_no_pending_violations_answer(fil_: str):
        return f'Перенесенных нарушений для филиала {fil_} нет'

    @staticmethod
    async def correct_mode(text_mes: str) -> str:
        res = f'Вы <b>в режиме исправления нарушения</b>:\n{text_mes}\nПожалуйста, приложите фотографию и добавьте комментарий в качестве подписи'
        return res

    @staticmethod
    async def pending_period(pending_date: dt.datetime) -> str:
        res = f"Вы выбрали срок переноса: <b>{pending_date.strftime('%d-%m-%Y')}</b>"
        return res


class MoControlerMessages:
    start_message = f'{form_greeting()}, куратор МО!'


class ToVacationMessages:
    back_to_menu = 'Возвращаемся в меню'
    choose_surname = 'Введите фамилию сотрудника'
    no_employee = 'Мы не нашли сотрудника с такой фамилией'
    to_vacation_success = 'Сотрудник в отпуске! Теперь он не будет получать оповещений и не будет иметь доступа к сервису ✅'

    from_vacation_success = 'Вернули сотрудника из отпуска! Теперь он имеет доступ к сервису ✅'

    no_user = 'Хм, не могу найти сотрудника. Попробуйте ещё раз ✅'
