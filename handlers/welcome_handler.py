import sqlite3
from random import randint

from aiogram import Router, F, Bot
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery

from states import Registration
from keyboards.simple_keyboard import make_inline_row_keyboard
from database.db_common import insert_data, display_all_data

from hidden.tokenfile import OWNER_CHAT_ID, TOKEN_FOUR

bot = Bot(TOKEN_FOUR)

router = Router()


@router.message(Command("start"))
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


@router.callback_query(F.data.in_(["Пройти регистрацию"]))
async def start_registration(callback: CallbackQuery, state: FSMContext):
    text = f'Пользователь {callback.from_user.username} (ID={callback.from_user.id}), нажал на кнопку'
    print(text)
    await bot.send_message(chat_id=OWNER_CHAT_ID, text=text)

    # Устанавливаем пользователю состояние "старт регистрации"
    await state.set_state(Registration.waiting_for_employee_code)

    await callback.message.answer(text="Введите 'Код сотрудника' (4 или 5 цифр)")


@router.message(Registration.waiting_for_employee_code)
async def handler_for_employee_code(message: Message, state: FSMContext):
    pass
    #TODO функция формальной проверки кода сотрудника



