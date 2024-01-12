from aiogram import Router, F, Bot
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery, InputFile, FSInputFile

from database.salary_table_functions import close_irrelevant_entries, return_the_receipt, get_one_record, \
    get_salary_password_for_user
from states import Registration
from keyboards.simple_keyboard import make_inline_row_keyboard
from database.general_db_functions import update_data_in_column, get_data_from_column
from database.user_table_functions import TABLE_NAME, get_user_state_from_db, insert_user_to_database, \
    get_user_employee_code_from_db

from hidden.tokenfile import TOKEN_FOUR
from encrypt.math_operations import check_employee_code
from database.user_table_functions import employee_code_not_registered

bot = Bot(TOKEN_FOUR)

router = Router()


# При получении файла, проверка статуса будет вызываться из хендлера salary.handle_excel_file
@router.message(StateFilter(None), ~F.document)
async def restoring_state_from_database(message: Message, state: FSMContext) -> None:
    """Функция восстанавливает state из БД и вызывает соответствующий обработчик данного state
    Это необходимый элемент корректной работы при перезапуске бота"""

    name_of_current_state = get_user_state_from_db(str(message.chat.id))
    print(f'Юзер {message.chat.id}: restoring_state_from_database. Текущий статус: {name_of_current_state}')
    if not name_of_current_state:
        await start_dialogue(message=message)
    else:
        current_state = f'Registration:{name_of_current_state}'
        await state.set_state(current_state)
        result = await state.get_state()
        print(f'Юзер {message.chat.id}: обновлен state из базы на {result}')

        if name_of_current_state == 'waiting_for_employee_code':
            await waiting_for_employee_code(message=message, state=state)

        elif name_of_current_state == 'waiting_for_secret_employee_code':
            await waiting_for_secret_employee_code(message=message, state=state)

        elif name_of_current_state == 'employee_is_registered':
            await employee_is_registered(message=message, state=state)

        elif name_of_current_state == 'employee_is_banned':
            await employee_is_banned(message=message)

        elif name_of_current_state == 'None':
            await start_dialogue(message=message)


@router.message(Command("start"), StateFilter(None))
async def start_dialogue(message: Message):
    """"""

    print(f'Юзер {message.chat.id}: start_dialogue')
    await message.answer(reply_markup=ReplyKeyboardRemove(), text='Добрый день!')

    record_of_user = (
        str(message.chat.id),  # telegram_id
        message.chat.username,  # telegram_username
        'None',  # state_in_bot
        '',  # employee_code
        '',  # secret_employee_code
        '3',  # registration_attempts
    )
    if insert_user_to_database(record_of_user):
        # Если данные для этого telegram_id были сохранены в БД только что (т.е. пользователь новый):
        await message.answer(
            text="Я робот-почтальон!\n"
                 "Меня создали для однонаправленной рассылки конфиденциальной информации нескольким адресатам.\n"
                 "Данная конфигурация предназначена для ежемесячного извещения сотрудников о результатах их работы",
        )
    else:
        # Если такой telegram_id уже был в базе:
        await message.answer(text='Рад снова Вас видеть!')

    await message.answer(
        text="Для регистрации Вам понадобится:\n"
             "- 'Код сотрудника' (на портале Компании),\n"
             "- 'Секретный код сотрудника' (получаете непосредственно из рук руководителя)",
        reply_markup=make_inline_row_keyboard(['Пройти регистрацию'])
    )

    await message.answer(text="Загружаю видео-демонстрацию (требуется 10-15 секунд)")
    video_path = "demo.mp4"  # Укажите правильный путь к видео
    video = FSInputFile(video_path)
    await message.answer_document(video)


# Фильтр "StateFilter(None)" для того, чтобы после однократного нажатия, кнопка перестала реагировать:
@router.callback_query(F.data.in_(["Пройти регистрацию"]), StateFilter(None))
async def start_registration(callback: CallbackQuery, state: FSMContext) -> None:
    """Функция выводит сообщение об ожидании ввода от пользователя 'кода сотрудника'
    и изменяет state на 'waiting_for_employee_code'"""

    await callback.answer()
    print(f'Юзер {callback.from_user.id}: нажал на кнопку "Пройти регистрацию"')

    # Устанавливаем пользователю состояние "Ожидание кода сотрудника"
    await state.set_state(Registration.waiting_for_employee_code)
    update_data_in_column(
        table_name=TABLE_NAME,
        base_column_name='telegram_id',
        base_column_value=str(callback.from_user.id),
        target_column_name='state_in_bot',
        new_value='waiting_for_employee_code',
    )
    await callback.message.answer(
        text="Введите 'Код сотрудника' (4-6 цифр)",
    )


@router.message(Registration.waiting_for_employee_code)
async def waiting_for_employee_code(message: Message, state: FSMContext) -> None:
    """Функция проверяет полученный 'код сотрудника' на возможность его конвертации в 'секретный код сотрудника', что
    является косвенным признаком корректного 'кода сотрудника'
    При удачно пройденной проверке, функция привязывает 'код сотрудника' к данному telegram_id"""

    print(f'Юзер {message.chat.id}: waiting_for_employee_code')

    # Пытаемся преобразовать "код сотрудника" в "секретный код сотрудника"
    secret_employee_code = check_employee_code(message.text)
    if secret_employee_code:
        # Проверяем "код сотрудника" на наличие в таблице зарегистрированных юзеров:
        code_not_registered = employee_code_not_registered(message.text)
        if code_not_registered:
            await message.answer(text="Отлично!\n"
                                      "Теперь введите 'Секретный код сотрудника. "
                                      "Как правило, он состоит из цифр, разделенных тире.\n"
                                      "Например: 1111-1111-1111-1111\n"
                                      "У Вас будет три попытки!",
                                 reply_markup=make_inline_row_keyboard(
                                     ["Изменить Код сотрудника"]))
            await state.set_state(Registration.waiting_for_secret_employee_code)
            update_data_in_column(
                table_name=TABLE_NAME,
                base_column_name='telegram_id',
                base_column_value=str(message.from_user.id),
                target_column_name='state_in_bot',
                new_value='waiting_for_secret_employee_code'
            )
            update_data_in_column(
                table_name=TABLE_NAME,
                base_column_name='telegram_id',
                base_column_value=str(message.from_user.id),
                target_column_name='employee_code',
                new_value=message.text
            )
            # Сохранение "Секретного кода сотрудника", полученного из функции шифрования "Кода сотрудника", в БД -
            # это защита от подбора значения на следующем шаге, где "Секретный код сотрудника" будет вводить юзер
            update_data_in_column(
                table_name=TABLE_NAME,
                base_column_name='telegram_id',
                base_column_value=str(message.from_user.id),
                target_column_name='secret_employee_code',
                new_value=secret_employee_code
            )
        # Если полученный от юзера "код сотрудника" уже зарегистрирован на другой telegram_id:
        else:
            await message.answer(text="Введенный 'Код сотрудника' уже зарегистрирован.\n"
                                      "Если это Ваш код, обратитесь к руководителю\n"
                                      "Если вы ошиблись, повторите ввод")
    # Если полученный от юзера "код сотрудника" не может быть преобразован в "секретный код сотрудника":
    else:
        await message.answer(text="Не могу разобрать Ваш 'Код сотрудника'.\n"
                                  "Напоминаю, что он состоит из 4-6 цифр.\n"
                                  "Попробуйте еще раз")


@router.message(Registration.waiting_for_secret_employee_code)
async def waiting_for_secret_employee_code(message: Message, state: FSMContext) -> None:
    """Функция сравнивает полученный от юзера 'секретный код сотрудника' со значением 'секретного кода сотрудника',
    которое получили зашифровав 'код сотрудника'"""

    print(f'Юзер {message.chat.id}: waiting_for_secret_employee_code')

    user_secret_employee_code = get_data_from_column(
        table_name=TABLE_NAME,
        base_column_name='telegram_id',
        base_column_value=str(message.chat.id),
        target_column_name='secret_employee_code'
    )[0]
    if message.text == user_secret_employee_code:
        await state.set_state(Registration.employee_is_registered)
        update_data_in_column(
            table_name=TABLE_NAME,
            base_column_name='telegram_id',
            base_column_value=str(message.from_user.id),
            target_column_name='state_in_bot',
            new_value='employee_is_registered'
        )
        await message.answer(text="Отлично!\nРегистрация прошла успешно.\n"
                                  "Если Вы руководитель, отправьте табель в виде файла Excel.\n"
                                  "Если Вы сотрудник, Вам придет уведомление, когда руководитель вышлет табель, "
                                  "но можно проверить, имеется ли уже сейчас актуальный квиток",
                             reply_markup=make_inline_row_keyboard(
                                 ["Запросить квиток"])
                             )

    else:
        # Если 'секретный код сотрудника' некорректный, уменьшаем счетчик попыток:
        registration_attempts = get_data_from_column(
            table_name=TABLE_NAME,
            base_column_name='telegram_id',
            base_column_value=str(message.chat.id),
            target_column_name='registration_attempts'
        )[0]
        registration_attempts = int(registration_attempts) - 1
        update_data_in_column(
            table_name=TABLE_NAME,
            base_column_name='telegram_id',
            base_column_value=str(message.from_user.id),
            target_column_name='registration_attempts',
            new_value=str(registration_attempts)
        )
        # Если счетчик попыток дошел до нуля, баним юзера:
        if int(registration_attempts) < 1:
            await state.set_state(Registration.employee_is_banned)
            update_data_in_column(
                table_name=TABLE_NAME,
                base_column_name='telegram_id',
                base_column_value=str(message.from_user.id),
                target_column_name='state_in_bot',
                new_value='employee_is_banned'
            )
            await message.answer(text=f"Вы исчерпали все попытки. Обратитесь к руководителю.")

        else:
            await message.answer(text=f"'Секретный код сотрудника' не соответствует коду сотрудника.\n"
                                      f"Осталось попыток: {registration_attempts}")


@router.callback_query(Registration.employee_is_registered, F.data.in_(["Запросить квиток"]))
async def check_the_receipt(callback: CallbackQuery, state: FSMContext) -> None:
    """Функция запускает проверку на наличие актуального квитка, в случае существования такого - запрашивает пароль"""

    await callback.answer()
    code = get_user_employee_code_from_db(telegram_id=str(callback.message.chat.id))
    record_is_exist = close_irrelevant_entries(employee_code=code)
    if record_is_exist:
        # Данный статус не сохраняется в БД как скоротечный
        await state.set_state(Registration.waiting_for_salary_code)
        await callback.message.answer(text='Обнаружен актуальный квиток. Введите заливочный пароль')
    else:
        await callback.message.answer(text='Квиток не обнаружен')


@router.message(Registration.waiting_for_salary_code)
async def check_salary_password(message: Message, state: FSMContext) -> None:
    # Сразу меняем статус назад до employee_is_registered. Если пароль верный - статус и так возвращать,
    # если пароль неверный, к сообщению о неверном пароле будет прикручена кнопка "Запросить квиток", обработчик которой
    # приведет статус к waiting_for_salary_code
    await state.set_state(Registration.employee_is_registered)

    code = get_user_employee_code_from_db(telegram_id=str(message.from_user.id))
    salary_password_from_bd = get_salary_password_for_user(employee_code=code)

    if message.text == salary_password_from_bd:
        await message.answer(text='Пароль верный!')
        text = return_the_receipt(employee_code=code)
        await message.answer(text=text)
    else:
        await message.answer(
            text='Пароль неверный, попробуйте еще раз',
            reply_markup=make_inline_row_keyboard(["Запросить квиток"]))


@router.message(Registration.employee_is_banned)
async def employee_is_banned(message: Message) -> None:
    """Функция, обрабатывающая юзера, если он забанен"""

    print(f'Юзер {message.chat.id}: employee_is_banned')

    await message.answer(text="Ничего не могу поделать. Обратитесь к руководителю. "
                              "Возможно, его заявку на обнуление бана одобрят")


@router.message(Registration.employee_is_registered, F.content_type.in_({'text', 'sticker', 'photo'}))
async def employee_is_registered(message: Message, state: FSMContext) -> None:
    """Автоответчик на сообщения зарегистрированного пользователя"""

    print(f'Юзер {message.from_user.id}: employee_is_registered')

    await state.set_state(Registration.employee_is_registered)
    await message.answer(text="Регистрация прошла успешно. Когда руководитель вышлет данные, Вам придет уведомление,"
                              "но можно проверить, имеется ли уже сейчас актуальный квиток",
                         reply_markup=make_inline_row_keyboard(["Запросить квиток"])
                         )


@router.callback_query(Registration.waiting_for_secret_employee_code, F.data.in_(["Изменить Код сотрудника"]))
async def cancel_registration(callback: CallbackQuery, state: FSMContext) -> None:
    """Функция возвращает пользователя на шаг ввода 'кода сотрудника', не обнуляя при этом количество попыток
    ввода 'секретного кода сотрудника'"""

    await callback.answer()
    print(f"Юзер {callback.from_user.id}: нажал на кнопку 'Изменить Код сотрудника'")

    await state.set_state(Registration.waiting_for_employee_code)
    update_data_in_column(
        table_name=TABLE_NAME,
        base_column_name='telegram_id',
        base_column_value=str(callback.from_user.id),
        target_column_name='employee_code',
        new_value=''
    )
    update_data_in_column(
        table_name=TABLE_NAME,
        base_column_name='telegram_id',
        base_column_value=str(callback.from_user.id),
        target_column_name='secret_employee_code',
        new_value=''
    )
    update_data_in_column(
        table_name=TABLE_NAME,
        base_column_name='telegram_id',
        base_column_value=str(callback.from_user.id),
        target_column_name='state_in_bot',
        new_value='waiting_for_employee_code'
    )
    await callback.message.answer(
        text="Введите 'Код сотрудника' (4-6 цифр)",
    )
