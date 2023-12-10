from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


def make_replay_row_keyboard(items: list[str]) -> ReplyKeyboardMarkup:
    """
    Создаёт реплай-клавиатуру с кнопками в один ряд
    :param items: список текстов для кнопок
    :return: объект реплай-клавиатуры
    """
    row = [KeyboardButton(text=item) for item in items]
    return ReplyKeyboardMarkup(keyboard=[row], resize_keyboard=True)


def make_inline_row_keyboard(items: list[str]) -> InlineKeyboardMarkup:
    """
    Создаёт инлайн-клавиатуру с кнопками в один ряд
    :param items: список текстов для кнопок
    :return: объект реплай-клавиатуры
    """
    row = [InlineKeyboardButton(text=item, callback_data=item) for item in items]
    return InlineKeyboardMarkup(inline_keyboard=[row])


def make_inline_rows_keyboard(items: list[str]) -> InlineKeyboardMarkup:
    """
    Создаёт инлайн-клавиатуру с кнопками в несколько рядов по числу кнопок
    :param items: список текстов для кнопок
    :return: объект реплай-клавиатуры
    """
    rows = [[InlineKeyboardButton(text=str(item), callback_data=str(item))] for item in items]
    return InlineKeyboardMarkup(inline_keyboard=rows)


