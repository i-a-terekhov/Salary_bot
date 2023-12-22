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


def make_inline_many_keys_keyboard(items: list[str]) -> InlineKeyboardMarkup:
    """
    Создаёт инлайн-клавиатуру с кнопками в несколько рядов по четыре в ряд
    :param items: список текстов для кнопок
    :return: объект реплай-клавиатуры
    """
    # Разбиваем список на подсписки по 4 элемента
    rows = [items[i:i+4] for i in range(0, len(items), 4)]

    keyboard = [[InlineKeyboardButton(
                    text=str(item),
                    callback_data=f"view_{str(item)}"
                                    ) for item in row] for row in rows]

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def make_inline_secret_many_keys_keyboard(items: list[str]) -> InlineKeyboardMarkup:
    """
    Создаёт инлайн-клавиатуру с кнопками в несколько рядов по четыре в ряд
    первый и последний ряд - по одной кнопке
    :param items: список текстов для кнопок
    :return: объект реплай-клавиатуры
    """
    # Отбрасываем первый и последний элементы:
    cut_items = items[1:-1]

    # Разбиваем усеченный список на подсписки по 4 элемента
    stand_rows = [cut_items[i:i+4] for i in range(0, len(items), 4)]

    full_items = [[items[0]]]
    full_items.extend(stand_rows)
    full_items.extend([[items[-1]]])

    keyboard = [[InlineKeyboardButton(
                    text=str(item),
                    callback_data=f"secret_{str(item)}"
                                    ) for item in row] for row in full_items]

    return InlineKeyboardMarkup(inline_keyboard=keyboard)

