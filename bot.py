import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from hidden.tokenfile import TOKEN_FOUR
from handlers import welcome_handler, stop, salary

from database.general_db_functions import test_connection, display_all_data_from_table
from database.user_table_functions import TABLE_NAME, REGISTRATION_TABLE


bot_unit = Bot(TOKEN_FOUR)

if not test_connection(table_name=TABLE_NAME, required_columns=REGISTRATION_TABLE):
    input('Продолжать?')

print(f'Состояние БД, таблица {TABLE_NAME}, при запуске:')
display_all_data_from_table(table_name=TABLE_NAME)


async def main(bot):
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )

    dp = Dispatcher(
        storage=MemoryStorage(),
        maintenance_mode=False
    )

    dp.include_routers(
        welcome_handler.router,
        salary.router,
        # stop.boring_router, stop.regular_router,
    )

    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main(bot=bot_unit))
