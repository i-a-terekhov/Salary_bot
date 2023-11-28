import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from hidden.tokenfile import TOKEN_FOUR
from handlers import stop, salary

bot_unit = Bot(TOKEN_FOUR)


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
        # salary.router,
        stop.boring_router, stop.regular_router,
    )

    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main(bot=bot_unit))
