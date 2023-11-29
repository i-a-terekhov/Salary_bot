from aiogram import Bot, Router, F
from aiogram.filters import MagicData, CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from hidden.tokenfile import OWNER_CHAT_ID, TOKEN_FOUR


# Хэндлеры этого роутера перехватят все сообщения и колбэки,
# если атрибут maintenance_mode на диспетчере переключить в то же положение,
# которое установлено в роутере (в данном примере - True)
boring_router = Router()
boring_router.message.filter(MagicData(F.maintenance_mode.is_(True)))
boring_router.callback_query.filter(MagicData(F.maintenance_mode.is_(True)))

# Хэндлеры этого роутера используются ВНЕ режима обслуживания,
# т.е. когда maintenance_mode на диспетчере равен False или не указан вообще
regular_router = Router()

bot = Bot(TOKEN_FOUR)


@boring_router.message()
async def any_message(message: Message):
    text = f'Пользователь {message.from_user.username} (ID={message.from_user.id}), заинтересовался ботом'
    print(text)
    await bot.send_message(chat_id=OWNER_CHAT_ID, text=text)
    await message.answer("Бот в режиме обслуживания. Пожалуйста, подождите.")


@boring_router.callback_query()
async def any_callback(callback: CallbackQuery):
    text = f'Пользователь {callback.from_user.username} (ID={callback.from_user.id}), заинтересовался ботом'
    print(text)
    await bot.send_message(chat_id=OWNER_CHAT_ID, text=text)
    await callback.answer(
        text="Бот в режиме обслуживания. Пожалуйста, подождите",
        show_alert=True
    )


# ----------------------------------------------------------------------------------------------------------------------
@regular_router.message(CommandStart())
async def cmd_start(message: Message):
    text = f'Пользователь {message.from_user.username} (ID={message.from_user.id}), заинтересовался ботом'
    print(text)
    await bot.send_message(chat_id=OWNER_CHAT_ID, text=text)
    builder = InlineKeyboardBuilder()
    builder.button(text="Нажми меня, чтобы убедиться", callback_data="anything")
    await message.answer(
        text="Бот в разработке, т.е. пока не работает",
        reply_markup=builder.as_markup()
    )


@regular_router.message(F.document != None)
async def catch_document(message: Message):
    text = f'Пользователь {message.from_user.username} (ID={message.from_user.id}) прислал документ:'
    print(text, message.document.file_name)
    await bot.send_message(chat_id=OWNER_CHAT_ID, text=text)
    await bot.send_document(chat_id=OWNER_CHAT_ID, document=message.document.file_id, caption=message.caption)

    builder = InlineKeyboardBuilder()
    builder.button(text="Нажми меня, чтобы убедиться", callback_data="anything")
    await message.answer(
        text="Бот в разработке, т.е. пока не работает",
        reply_markup=builder.as_markup()
    )


@regular_router.message()
async def catch_any_types(message: Message):
    text = f'Пользователь {message.from_user.username} (ID={message.from_user.id}) прислал прочее сообщение:'
    print(text, message.text)
    await bot.send_message(chat_id=OWNER_CHAT_ID, text=text)
    await bot.forward_message(chat_id=OWNER_CHAT_ID, from_chat_id=message.chat.id, message_id=message.message_id)

    builder = InlineKeyboardBuilder()
    builder.button(text="Нажми меня, чтобы убедиться", callback_data="anything")
    await message.answer(
        text="Бот в разработке, т.е. пока не работает",
        reply_markup=builder.as_markup())


@regular_router.callback_query(F.data.in_(["anything", "Регистрация", "Log in", "Кнопка не работает"]))
async def callback_anything(callback: CallbackQuery):
    text = f'Пользователь {callback.from_user.username} (ID={callback.from_user.id}), нажал на кнопку'
    print(text)
    await bot.send_message(chat_id=OWNER_CHAT_ID, text=text)
    await callback.answer(
        text="Кнопка, очевидно, пока не работает :(",
        show_alert=True
    )
