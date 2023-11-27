from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup


class Registration(StatesGroup):
    waiting_for_name = State()
    waiting_for_email = State()


@dp.message_handler(commands=['start'])
async def start_registration(message: types.Message):
    await Registration.waiting_for_name.set()
    await message.reply("Привет! Как тебя зовут?")


@dp.message_handler(state=Registration.waiting_for_name)
async def process_name(message: types.Message, state: FSMContext):
    user_name = message.text

    # Сохранение данных в состояние
    await state.update_data(name=user_name)

    await Registration.waiting_for_email.set()
    await message.reply("Отлично! Теперь укажи свой email.")

@dp.message_handler(state=Registration.waiting_for_email)
async def process_email(message: types.Message, state: FSMContext):
    # Получение данных из состояния
    user_data = await state.get_data()
    user_email = message.text

    # Доступ к данным, сохраненным в предыдущем состоянии
    user_name = user_data.get('name', 'Unknown')

    await state.finish()  # Завершение состояния

    await message.reply(f"Спасибо, {user_name}! Твой email: {user_email}")
