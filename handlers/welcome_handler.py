import sqlite3
from random import randint

from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove

from states import CommonStart
from keyboards.simple_keyboard import make_inline_row_keyboard
from database.db_common import insert_data, display_all_data, drop_columns

router = Router()


@router.message(Command("start"))
async def start_dialogue(message: Message, state: FSMContext):
    await message.answer(reply_markup=ReplyKeyboardRemove(), text='Добрый день!')

    new_record = (
        str(message.chat.id),
        message.chat.username,
        'waiting_for_start',
        'employee_code',
        'secret_employee_code',
    )
    if insert_data(new_record):
        await message.answer(
            text="Я робот-почтальон! Чтобы получать письма от вашего руководителя пройдите регистрацию",
            reply_markup=make_inline_row_keyboard(['Кнопка не работает'])
        )
        # Устанавливаем пользователю состояние "старт регистрации"
        await state.set_state(CommonStart.waiting_for_start)
    else:
        await message.answer(text='Рад снова Вас видеть!')
    print('ИТОГ:')
    display_all_data()
