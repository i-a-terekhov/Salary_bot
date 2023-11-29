import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from hidden.tokenfile import TOKEN_FOUR
from database import db_common
from handlers import welcome_handler, stop, salary


bot_unit = Bot(TOKEN_FOUR)

if not db_common.test_connection():
    input('Продолжать?')

db_common.display_all_data()


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
        # salary.router,
        stop.boring_router, stop.regular_router,
    )

    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main(bot=bot_unit))
