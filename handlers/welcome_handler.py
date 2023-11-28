import sqlite3
from random import randint

from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove

from states import CommonStart
from keyboards.simple_keyboard import make_inline_row_keyboard
from database.db_common import insert_data, display_all_data

router = Router()


@router.message(Command("start"))
async def start_dialogue(message: Message, state: FSMContext):
    await message.answer(reply_markup=ReplyKeyboardRemove(), text='Добрый день!')

    text_random = str(randint(56566, 56569))
    if insert_data(message.chat.id, message.from_user.username, 'еще текст'):
        await message.answer(
            text="Я робот-почтальон! Чтобы получать письма от вашего руководителя пройдите регистрацию",
            reply_markup=make_inline_row_keyboard(['первый', 'второй'])
        )
        # Устанавливаем пользователю состояние "старт регистрации"
        await state.set_state(CommonStart.waiting_for_start)
    else:
        await message.answer(text='Рад снова Вас видеть!')

    display_all_data()
