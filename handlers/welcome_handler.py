import sqlite3
from random import randint
from typing import Dict, Any

from aiogram import Router, F, Bot
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery

from states import Registration
from keyboards.simple_keyboard import make_inline_row_keyboard
from database.db_common import insert_user_to_database, update_data_in_column, get_user_state_from_db, \
    get_data_from_column

from hidden.tokenfile import TOKEN_FOUR
from encrypt.math_operations import check_employee_code

bot = Bot(TOKEN_FOUR)

router = Router()


@router.message(StateFilter(None))
async def restoring_state_from_database(message: Message, state: FSMContext):
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
            await employee_is_registered(message=message)

        elif name_of_current_state == 'employee_is_banned':
            await employee_is_banned(message=message)


@router.message(Command("start"), StateFilter(None))
async def start_dialogue(message: Message):
    print(f'Юзер {message.chat.id}: start_dialogue')
    await message.answer(reply_markup=ReplyKeyboardRemove(), text='Добрый день!')

    record_of_user = (
        str(message.chat.id),
        message.chat.username,
        '',  # state_in_bot
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


# Фильтр "StateFilter(None)" для того, чтобы после однократного нажатия, кнопка перестала реагировать:
@router.callback_query(F.data.in_(["Пройти регистрацию"]), StateFilter(None))
async def start_registration(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    print(f'Юзер {callback.from_user.id}: нажал на кнопку "Пройти регистрацию"')

    # Проверяем запись юзера. На случай, если в чате сохранилась кнопка "Пройти регистрацию", а юзер был удален из базы.
    record_of_user = (
        str(callback.from_user.id),
        callback.from_user.username,
        'waiting_for_employee_code',  # state_in_bot
        '',  # employee_code
        '',  # secret_employee_code
        '3',  # registration_attempts
    )
    insert_user_to_database(record_of_user)
    print(f'Юзер {callback.from_user.id}: restoring_state_from_database. Текущий статус: waiting_for_employee_code')

    # Устанавливаем пользователю состояние "Ожидание кода сотрудника"
    await state.set_state(Registration.waiting_for_employee_code)
    update_data_in_column(
        telegram_id=str(callback.from_user.id),
        column='state_in_bot',
        value='waiting_for_employee_code'
    )
    await callback.message.answer(
        text="Введите 'Код сотрудника' (4-6 цифр)",
    )


@router.message(Registration.waiting_for_employee_code)
async def waiting_for_employee_code(message: Message, state: FSMContext):
    print(f'Юзер {message.chat.id}: waiting_for_employee_code')

    secret_employee_code = check_employee_code(message.text)
    if secret_employee_code:
        await message.answer(text="Отлично!\n"
                                  "Теперь введите 'Секретный код сотрудника."
                                  "Как правило, он состоит из цифр, разделенных тире.\n"
                                  "Например: 1111-1111-1111-1111\n"
                                  "У Вас будет три попытки!",
                             reply_markup=make_inline_row_keyboard(
                                 ["Изменить Код сотрудника"]))
        await state.set_state(Registration.waiting_for_secret_employee_code)
        update_data_in_column(
            telegram_id=str(message.from_user.id),
            column='state_in_bot',
            value='waiting_for_secret_employee_code'
        )
        update_data_in_column(
            telegram_id=str(message.from_user.id),
            column='employee_code',
            value=message.text
        )
        # Сохраннение "Секретного кода сотрудника", полученного из функции шифрования "Кода сотрудника", В БД -
        # это защита от подбора значения на следующем шаге, где "Секретный код сотрудника" будет вводить юзер
        update_data_in_column(
            telegram_id=str(message.from_user.id),
            column='secret_employee_code',
            value=secret_employee_code
        )
    else:
        await message.answer(text="Не могу разобрать Ваш 'Код сотрудника'.\n"
                                  "Напоминаю, что он состоит из 4-6 цифр.\n"
                                  "Попробуйте еще раз")


@router.message(Registration.waiting_for_secret_employee_code)
async def waiting_for_secret_employee_code(message: Message, state: FSMContext):
    print(f'Юзер {message.chat.id}: waiting_for_secret_employee_code')

    user_secret_employee_code = get_data_from_column(telegram_id=str(message.chat.id), column='secret_employee_code')
    if message.text == user_secret_employee_code:
        await message.answer(text="Отлично!\n"
                                  "Регистрация прошла успешно.\n "
                                  "Если Вы руководитель, отправьте табель в виде файла Excel.\n"
                                  "Когда Вы сотрудник, Вам придет уведомление, когда руководитель вышлет табель")
        await state.set_state(Registration.employee_is_registered)
        update_data_in_column(
            telegram_id=str(message.from_user.id),
            column='state_in_bot',
            value='employee_is_registered'
        )
        # TODO здесь можно поместить кнопку "запросить квиток"
    else:
        registration_attempts = get_data_from_column(telegram_id=str(message.chat.id), column='registration_attempts')
        registration_attempts = int(registration_attempts) - 1
        update_data_in_column(telegram_id=str(message.from_user.id),
                              column='registration_attempts',
                              value=str(registration_attempts))

        if int(registration_attempts) < 1:
            await state.set_state(Registration.employee_is_banned)
            update_data_in_column(
                telegram_id=str(message.from_user.id),
                column='state_in_bot',
                value='employee_is_banned'
            )
            await message.answer(text=f"Вы исчерпали все попытки. Обратитесь к руководителю.")

        else:
            await message.answer(text=f"'Секретный код сотрудника' не соответствует коду сотрудника.\n"
                                      f"Осталось попыток: {registration_attempts}",
                                 reply_markup=make_inline_row_keyboard(
                                     ["Изменить Код сотрудника"])
                                 )


@router.message(Registration.employee_is_banned)
async def employee_is_banned(message: Message):
    print(f'Юзер {message.chat.id}: employee_is_banned')

    await message.answer(text="Ничего не могу поделать. Обратитесь к руководителю. "
                              "Возможно, его заявку на обнуление бана одобрят")


@router.message(Registration.employee_is_registered)
async def employee_is_registered(message: Message, state: FSMContext):
    print(f'Юзер {message.from_user.id}: employee_is_registered')

    await state.set_state(Registration.employee_is_registered)
    await message.answer(text="Регистрация прошла успешно. Когда руководитель вышлет данные, Вам придет уведомление")


@router.callback_query(Registration.waiting_for_secret_employee_code, F.data.in_(["Изменить Код сотрудника"]))
async def cancel_registration(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    print(f"Юзер {callback.from_user.id}: нажал на кнопку 'Изменить Код сотрудника'")

    await state.set_state(Registration.waiting_for_employee_code)
    update_data_in_column(
        telegram_id=str(callback.from_user.id),
        column='state_in_bot',
        value='waiting_for_employee_code'
    )
    await callback.message.answer(
        text="Введите 'Код сотрудника' (4-6 цифр)",
    )
