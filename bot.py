import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

import database.general_db_functions
from hidden.tokenfile import TOKEN_FOUR
from database import db_common
from handlers import welcome_handler, stop, salary

from database.general_db_functions import test_connection


bot_unit = Bot(TOKEN_FOUR)

if not test_connection(table_name="users", required_columns=('telegram_id', 'telegram_username', 'state_in_bot',
                                                             'employee_code', 'secret_employee_code',
                                                             'registration_attempts')
                       ):
    input('Продолжать?')

print('Состояние БД при запуске:')
database.general_db_functions.display_all_data()


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
