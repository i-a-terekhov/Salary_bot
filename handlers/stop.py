from aiogram import Router, F
from aiogram.filters import MagicData, CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder


# Хэндлеры этого роутера перехватят все сообщения и колбэки,
# если maintenance_mode равен True
maintenance_router = Router()
maintenance_router.message.filter(MagicData(F.maintenance_mode.is_(True)))
maintenance_router.callback_query.filter(MagicData(F.maintenance_mode.is_(True)))

regular_router = Router()


@maintenance_router.message()
async def any_message(message: Message):
    await message.answer("Бот в режиме обслуживания. Пожалуйста, подождите.")


@maintenance_router.callback_query()
async def any_callback(callback: CallbackQuery):
    await callback.answer(
        text="Бот в режиме обслуживания. Пожалуйста, подождите",
        show_alert=True
    )


# Хэндлеры этого роутера используются ВНЕ режима обслуживания,
# т.е. когда maintenance_mode равен False или не указан вообще
@regular_router.message(CommandStart())
async def cmd_start(message: Message):
    builder = InlineKeyboardBuilder()
    builder.button(text="Нажми меня", callback_data="anything")
    await message.answer(
        text="Бот в разработке, т.е. пока не работает",
        reply_markup=builder.as_markup()
    )


@regular_router.callback_query(F.data == "anything")
async def callback_anything(callback: CallbackQuery):
    await callback.answer(
        text="Кнопка, очевидно, пока тоже не работает :(",
        show_alert=True
    )
