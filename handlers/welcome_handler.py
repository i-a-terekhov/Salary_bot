import sqlite3

from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove

from states import CommonStart
from keyboards.simple_keyboard import make_inline_row_keyboard

from bot import DATABASE_NAME


DATABASE_NAME = DATABASE_NAME
connect = sqlite3.connect(DATABASE_NAME)


router = Router()


def insert_data(user_id, state, employee_data):
    # Создаем базу данных, если она не существует
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    # Проверяем наличие данных для указанного user_id
    select_query = 'SELECT * FROM users WHERE user_id = ?'
    cursor.execute(select_query, (user_id,))
    existing_data = cursor.fetchone()

    if existing_data:
        print(f"Данные для user_id {user_id} уже существуют. Ничего не вставлено.")
    else:
        # Данных нет, вставляем новую запись
        insert_query = 'INSERT INTO users (user_id, state, employee_data) VALUES (?, ?, ?)'
        cursor.execute(insert_query, (user_id, state, employee_data))
        print(f"Данные для user_id {user_id} успешно вставлены.")

    # Фиксируем изменения и закрываем соединение
    conn.commit()
    conn.close()


@router.message(Command("start"))
async def start_dialogue(message: Message, state: FSMContext):
    await message.answer(reply_markup=ReplyKeyboardRemove(), text='Добрый день!')
    await message.answer(
        text="Я робот-почтальон! Чтобы получать письма от вашего руководителя пройдите регистрацию",
        reply_markup=make_inline_row_keyboard(['первый', 'второй'])
    )
    # Устанавливаем пользователю состояние "старт регистрации"
    await state.set_state(CommonStart.waiting_for_start)

    insert_data(1, 'State1', 'EmployeeData1')
    insert_data(2, 'State2', 'EmployeeData2')


