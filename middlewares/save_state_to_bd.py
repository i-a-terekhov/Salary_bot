import sqlite3
from aiogram import BaseMiddleware
from database.db_common import DATABASE_REG_NAME
from aiogram.types import Message


# Использование middleware для подключения к базе данных:

# TODO перепроверить этот продукт генерации
class DbConnectionMiddleware(BaseMiddleware):
    async def __call__(self, message: Message, *args, **kwargs):
        print('Работает мидлварь DbConnectionMiddleware')
        setattr(message, "conn", sqlite3.connect(DATABASE_REG_NAME))
        setattr(message, "cursor", message.conn.cursor())
        await super().__call__(*args, **kwargs)


# Использование middleware для сохранения состояний в базе данных:
class DbSessionMiddleware(BaseMiddleware):
    async def __call__(self, message: Message, *args, **kwargs):
        print('Работает мидлварь DbSessionMiddleware')
        message["conn"] = sqlite3.connect(DATABASE_REG_NAME)
        message["cursor"] = message["conn"].cursor()
        await super().__call__(*args, **kwargs)



