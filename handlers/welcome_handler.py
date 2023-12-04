import sqlite3
from random import randint
from typing import Dict, Any

from aiogram import Router, F, Bot
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery

from states import Registration
from keyboards.simple_keyboard import make_inline_row_keyboard
from database.db_common import insert_data, display_all_data, update_data_in_column

from hidden.tokenfile import OWNER_CHAT_ID, TOKEN_FOUR
from encrypt.math_operations import check_employee_code

bot = Bot(TOKEN_FOUR)

router = Router()

#TODO необходима функция для переноса состояний из БД в оперативку бота (чтобы при перезагрузке бота не было проблем)

#TODO пишем хендлер для состояния None с обращением в БД для актуализации статуса. В этом же хендлере запускаем функцию,
# которая будет соответствовать найденному в БД stat'у


@router.message(Command("start"), StateFilter(None))
async def start_dialogue(message: Message):
    await message.answer(reply_markup=ReplyKeyboardRemove(), text='Добрый день!')

    new_record = (
        str(message.chat.id),
        message.chat.username,
        '',  # state_in_bot
        '',  # employee_code
        '',  # secret_employee_code
    )
    if insert_data(new_record):
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
    print('ИТОГ:')
    display_all_data()


@router.callback_query(F.data.in_(["Пройти регистрацию"]), StateFilter(None))
async def start_registration(callback: CallbackQuery, state: FSMContext):
    text = f'Пользователь {callback.from_user.username} (ID={callback.from_user.id}), нажал на кнопку'
    print(text)
    await bot.send_message(chat_id=OWNER_CHAT_ID, text=text)

    # Устанавливаем пользователю состояние "старт регистрации"
    await state.set_state(Registration.waiting_for_employee_code)
    update_data_in_column(
        telegram_id=str(callback.from_user.id), column='state_in_bot', value='waiting_for_employee_code'
    )
    await callback.message.answer(
        text="Введите 'Код сотрудника' (4-6 цифр)",
        reply_markup=make_inline_row_keyboard(['Вернуться в самое начало'])  #TODO добавить обработку
    )


@router.message(Registration.waiting_for_employee_code)
async def handler_for_employee_code(message: Message, state: FSMContext):
    secret_employee_code = check_employee_code(message.text)
    if secret_employee_code:
        await message.answer(text="Отлично!\n"
                                  "Теперь введите 'Секретный код сотрудника."
                                  "Как правило, он состоит из цифр, разделенных тире.\n"
                                  "Например: 1111-1111-1111-11",
                             reply_markup=make_inline_row_keyboard(['Вернуться в самое начало']))  #TODO добавить обработку)
        name_next_state = 'waiting_for_secret_employee_code'
        next_state = f'Registration.{name_next_state}'
        await state.set_state(next_state)
        update_data_in_column(
            telegram_id=str(message.from_user.id), column='state_in_bot', value='waiting_for_secret_employee_code'
        )
        await state.update_data(user_employee_code=message.text)
        await state.update_data(user_secret_employee_code=secret_employee_code)
    else:
        await message.answer(text="Не могу разобрать Ваш 'Код сотрудника'.\n"
                                  "Напоминаю, что он состоит из 4-6 цифр.\n"
                                  "Попробуйте еще раз")


@router.message(Registration.waiting_for_secret_employee_code)
async def handler_for_secret_employee_code(message: Message, state: FSMContext):
    data = await state.get_data()
    user_secret_employee_code = data['user_secret_employee_code']
    if message.text == user_secret_employee_code:
        await message.answer(text="Отлично!\n"
                                  "'Секретный код сотрудника' принят.")
        await state.set_state(Registration.employee_is_registered)
        update_data_in_column(
            telegram_id=str(message.from_user.id), column='state_in_bot', value='employee_is_registered'
        )
    else:
        await message.answer(text="Не могу разобрать Ваш 'Секретный код сотрудника'.\n"
                                  "Напоминаю, что он состоит из цифр, разделенных тире.\n"
                                  "Например: 1111-1111-1111-11")


@router.message(Registration.employee_is_registered)  # TODO можно удалить
async def proverka(message: Message):
    await message.answer(text="Регистрация прошла успешно")


@router.callback_query(F.data.in_(["Вернуться в самое начало"]))
async def cancel_registration(callback: CallbackQuery, state: FSMContext):
    text = f'Пользователь {callback.from_user.username} (ID={callback.from_user.id}), нажал на кнопку'
    print(text)
    await bot.send_message(chat_id=OWNER_CHAT_ID, text=text)

    # Устанавливаем пользователю состояние "старт регистрации"
    await state.set_state(Registration.waiting_for_employee_code)
    update_data_in_column(
        telegram_id=str(callback.from_user.id), column='state_in_bot', value='waiting_for_employee_code'
    )
    await callback.message.answer(
        text="Введите 'Код сотрудника' (4-6 цифр)",
    )







