from aiogram.fsm.context import FSMContext
from aiogram import BaseMiddleware

from database.db_common import DATABASE_REG_NAME
from aiogram.types import Message

from database.db_common import get_user_state_from_db, save_user_state_to_db


# Использование middleware для подключения к базе данных:


# TODO перепроверить этот продукт генерации
class SetStateFromDB(BaseMiddleware):
    async def set_user_state(self, message: Message, state: FSMContext):
        # Получаем состояние пользователя из БД
        telegram_id = message.from_user.id
        user_state = get_user_state_from_db(str(telegram_id))

        # Устанавливаем состояние в контексте
        if user_state:
            current_state = state.get_state()
            print(f'Меняем состояние с {current_state} на {user_state}')
            await state.set_state(user_state)


# Использование middleware для сохранения состояний в базе данных:
class SaveStateToDB(BaseMiddleware):
    async def save_user_state(self, message: Message, state: FSMContext):
        # Сохраняем текущее состояние пользователя в БД
        telegram_id = message.from_user.id
        current_state = await state.get_state()
        save_user_state_to_db(str(telegram_id), current_state)





