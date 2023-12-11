from pprint import pprint

from aiogram import Bot, Router, F, types
from aiogram.types import Message, CallbackQuery

from hidden.tokenfile import TOKEN_FOUR, OWNER_CHAT_ID

import openpyxl
from openpyxl import Workbook
from openpyxl import load_workbook

from keyboards.simple_keyboard import make_inline_many_keys_keyboard, make_inline_rows_keyboard
from states import Registration

router = Router()
bot = Bot(TOKEN_FOUR)

# Для поиска нужного листа мотивации ищем на каждом листе в диапазоне А1:С3 значение:
try_sheet_factor = 'Мотивация по не  учетным данным'

# Определение начального диапазона целевого листа для поиска нужных столбцов (код сотрудника, ЗП, премия и пр.)
start_cell = "A1"
end_cell = "I210"

# Получение численных значений для столбцов и строк
start_col = openpyxl.utils.column_index_from_string(start_cell[:1])
start_row = int(start_cell[1:])
end_col = openpyxl.utils.column_index_from_string(end_cell[:1])
end_row = int(end_cell[1:])

base_column = "Код."
target_column_01 = "Должность"
target_column_02 = "Ф.И.О."
target_column_03 = "Итог З/П"  # Оклад
target_column_04 = "Итог мотивация"  # Премия
target_column_05 = "Итог З\П+Бонус"  # Всего
target_column_06 = "Премия(компенсация отпуска)"
target_column_07 = "Вычеты ОС(форма/прочее)"
target_column_08 = "Вычеты ОС(Инвентаризация)"
target_column_09 = 'Вычеты-штрафы'
target_column_10 = 'Факт часы'
target_column_11 = 'Кол-во ошибок (примечание)'
target_column_12 = 'Сумма ошибки'
target_column_13 = 'Единый коэфф.'
target_column_14 = 'Дополнительные работы Н/Ч'
target_column_15 = 'Выдача '
target_column_16 = 'Доставки(Подготовка отгрузок)'
target_column_17 = 'Приемка'
target_column_18 = 'Размещение'
target_column_19 = 'Объем М3 кросс.'
target_column_20 = 'Сборка отгрузок'

target_columns = [target_column_01, target_column_02, target_column_03, target_column_04, target_column_05,
                  target_column_06, target_column_07, target_column_08, target_column_09, target_column_10,
                  target_column_11, target_column_12, target_column_13, target_column_14, target_column_15,
                  target_column_16, target_column_17, target_column_18, target_column_19, target_column_20]

offset_columns = [target_column_15, target_column_16, target_column_17,
                  target_column_18, target_column_19, target_column_20]
amount_of_indentation = 12

dict_of_persons = {}


async def delete_some_messages(chat_id: int, numbers_of_message: list[int]):
    for num in numbers_of_message:
        await bot.delete_message(chat_id=chat_id, message_id=num)


def search_salary_value(target_sheet, base_cell_name=base_column):
    global dict_of_persons
    # Ищем базовую ячейку (шапку базового столбца) в диапазоне start_cell:end_cell
    head_of_base_column = None
    for row in target_sheet.iter_rows(min_row=start_row, max_row=end_row, min_col=start_col, max_col=end_col):
        for cell in row:
            if cell.value == base_cell_name:
                head_of_base_column = cell
                break
        if head_of_base_column:
            break
    # Если базовая ячейка (шапка базового столбца) найдена, считаем, что найден лист с таблицей, ищем целевые столбцы:
    if target_sheet:
        dict_of_persons = {}

        for target in target_columns:
            search_values_of_one_target_column(
                base_column_head=head_of_base_column, target_sheet=target_sheet,
                target_column_name=target
            )


def forming_small_results_of_table() -> str:
    global dict_of_persons
    """
    Формирует краткий текст для подтверждения заливки руководителем.
    В данном случае, в формате: "Фамилия: итог ЗП"
    """
    text = ''
    for person_no in dict_of_persons:

        surname = str(dict_of_persons[person_no]["Ф.И.О."]).split(' ')[0]
        if len(surname) < 15:
            extra_space = 15 - len(surname)
            surname += ' ' * extra_space

        summ = dict_of_persons[person_no][target_column_05]

        text += f'{surname}{summ:_} руб.\n'
    print(text)
    return text


@router.callback_query(F.data.in_(["Посмотреть квиток"]))
async def select_an_employee(callback: CallbackQuery) -> None:
    await callback.answer()
    global dict_of_persons
    names = [(dict_of_persons[person_no]["Ф.И.О."]).split(' ')[0] for person_no in dict_of_persons]

    await callback.message.answer(
        text='Выберите сотрудника',
        reply_markup=make_inline_many_keys_keyboard(names)
    )


@router.callback_query(F.data.startswith("view_"))
async def forming_results_for_one_employee(callback: CallbackQuery):
    await callback.answer()
    _, last_name = callback.data.split('_')
    await callback.message.answer(text=f'Получен запрос на квиток для {last_name}')

    output_order_one = ['Ф.И.О.', 'Должность']
    output_order_two = ['Итог З/П', 'Итог мотивация', 'Итог З\\П+Бонус']
    output_order_three = ["Премия(компенсация отпуска)", "Вычеты ОС(форма/прочее)",
                          "Вычеты ОС(Инвентаризация)", 'Вычеты-штрафы', 'Дополнительные работы Н/Ч']
    output_order_four = ['Кол-во ошибок (примечание)', 'Сумма ошибки']
    output_order_five = ['Факт часы', 'Единый коэфф.', 'Выдача ', 'Доставки(Подготовка отгрузок)',
                         'Приемка', 'Размещение', 'Объем М3 кросс.', 'Сборка отгрузок']

    composed_text = ""
    for emp_id, emp_info in dict_of_persons.items():
        if emp_info.get('Ф.И.О.').split(' ')[0] == last_name:
            composed_text += f"\nКод сотрудника:\t{emp_id}:\n"
            for value in output_order_one:
                composed_text += f"{value}:\t{dict_of_persons[emp_id][value]}\n"
            composed_text += "-" * 50 + "\n"
            composed_text += f"ИТОГ ЗП:\t{dict_of_persons[emp_id][output_order_two[2]]} руб. ({dict_of_persons[emp_id][output_order_two[0]]} руб. + {dict_of_persons[emp_id][output_order_two[1]]} руб.)\n"
            composed_text += "-" * 50 + "\n"
            for value in output_order_three:
                composed_text += f"{value}:\t{dict_of_persons[emp_id][value]} руб.\n"
            composed_text += "-" * 50 + "\n"
            composed_text += f"Кол-во ошибок:\t{dict_of_persons[emp_id][output_order_four[0]]} (-{dict_of_persons[emp_id][output_order_four[1]]} руб.)\n"
            composed_text += "-" * 50 + "\n"
            for value in output_order_five:
                composed_text += f"{value}:\t{dict_of_persons[emp_id][value]}\n"

            break  # Прекращаем цикл, так как нашли нужного сотрудника

    print(composed_text)
    await callback.message.answer(text=composed_text)


def search_values_of_one_target_column(base_column_head, target_sheet, target_column_name) -> None:
    global dict_of_persons
    # Ищем целевой столбец.
    # Например, если базовый - "ID юзера", то целевым может быть - "Показатель" юзера по какому-то критерию
    target_column = None
    if base_column_head:
        # Проходим по ряду, в котором находятся истинные заголовки (строка 39:
        for col in target_sheet.iter_cols(min_row=39, max_row=39,
                                          min_col=base_column_head.column, max_col=target_sheet.max_column):

            # В каждом столбце всего одна строка, поэтому следующий цикл проходит один раз:
            for cell in col:
                target_column = False
                if cell.value == target_column_name:

                    # Если значение ячейки совпадает со столбцом, требующим сдвига, считаем det = 1, иначе det = 0:
                    if cell.value in offset_columns:
                        det = 1
                    else:
                        det = 0

                    # Проходим по строкам столбца col, добавляя каждую ячейку в target_column
                    target_column = tuple()
                    for cell_in_targ_col in target_sheet.iter_cols(min_row=base_column_head.row,
                                                                   max_row=target_sheet.max_row,
                                                                   min_col=col[0].column + amount_of_indentation * det,
                                                                   max_col=col[0].column + amount_of_indentation * det):
                        target_column += cell_in_targ_col

            # Прерываем цикл поиска целевого столбца, при первом найденном (ввиду дублирования наименования столбцов)
            if target_column:
                break

    # Если целевой столбец найден, выводим значения для непустых значений в базовом столбце
    if target_column:
        for cell in target_column:
            base_colum_value = target_sheet.cell(row=cell.row, column=base_column_head.column).value

            # Так же проверяем первые 4 символа (являются ли числами), чтобы отбросить строки-разделители
            if len(str(base_colum_value)) > 4 and str(base_colum_value)[:4].isdigit():

                # Добавляем значения в словарь
                if base_colum_value not in dict_of_persons:
                    dict_of_persons[base_colum_value] = {}
                dict_of_persons[base_colum_value][target_column_name] = cell.value

    # После полного формирования словаря, обнуляем значения строчных показателей для должностей с нестрочной мотивацией:
    positions_to_reset = ['Начальник склада', 'Заместитель начальника склада', 'Логист-претензионист',
                          'Супервизор', 'Старший кладовщик', 'Диспетчер', 'Старший оператор склада', 'Оператор склада']
    keys_to_reset = ['Выдача ', 'Доставки(Подготовка отгрузок)', 'Приемка', 'Размещение', 'Объем М3 кросс.',
                     'Сборка отгрузок']
    for key, data in dict_of_persons.items():
        position = data.get('Должность', '')
        if position in positions_to_reset:
            for key_to_reset in keys_to_reset:
                data[key_to_reset] = None


# Когда руководитель подтверждает суммы, бот просит его придумать пароль для этой конкретной заливки
# TODO функция, проверяющая "секретный зарплатный код" для конкретной заливки

# Когда ЗП-пароль установлен, данные перемещаются в БД, а руководителю высылаются секретные коды сотрудников
# TODO функция, высылающая руководителю файл(?) с секретными кодами сотрудников после заливки
# TODO функция, формирующая записи в зарплатной таблице (с секртеным кодом, "попыток ввода", датой заливки, "доступом" и пр. доп. столбцами)

# При подтверждении заливки данных, все сообщения с общими суммами и квитками должны удаляться


@router.message(F.document.file_name.endswith('.xlsx'), Registration.employee_is_registered)
async def handle_excel_file(message: types.Document):
    # Оповещение
    text = f'Юзер {message.from_user.id} прислал зарплатную ведомость'
    print(text)
    # await bot.send_document(chat_id=OWNER_CHAT_ID, document=message.document.file_id, caption=message.caption)

    # Получаем информацию о файле
    file_info = await bot.get_file(message.document.file_id)
    file = await bot.download_file(file_info.file_path)

    # Открываем файл с помощью openpyxl
    wb = openpyxl.load_workbook(file)

    # Перебираем все листы
    target_sheet = None
    for sheet_name in wb.sheetnames:
        sheet = wb[sheet_name]

        # Проверяем условие на каждом листе
        for row in sheet.iter_rows(min_row=1, max_row=3, min_col=1, max_col=3):
            for cell in row:
                if cell.value == try_sheet_factor:
                    # На первом листе, удовлетворяющем условию, останавливаем перебор:
                    target_sheet = sheet
                    break
        if target_sheet:
            break

    if target_sheet:
        # Используем target_sheet для дальнейших действий
        search_salary_value(target_sheet=target_sheet, base_cell_name=base_column)
        text = forming_small_results_of_table()
        if not text:
            text = 'Ничего не найдено'
            await bot.send_message(chat_id=message.from_user.id, text=text)
        else:
            await delete_some_messages(chat_id=message.chat.id, numbers_of_message=[message.message_id])
            await bot.send_message(chat_id=message.from_user.id, text='В Вашем файле я обнаружил зарплатную таблицу. '
                                                                      'Вот краткие итоги, чтобы проверить суммы:')
            await bot.send_message(chat_id=message.from_user.id, text=text)

            await bot.send_message(
                chat_id=message.from_user.id, text='Готовы разослать эти данные?',
                reply_markup=make_inline_rows_keyboard(["Да, выслать данные", "Посмотреть квиток", "Отменить"]))

        # TODO здесь должна быть кнопки "Да, выслать данные" и "Посмотреть как будет выглядеть квиток"
        # TODO Прикрутить кнопку "Отменить", которая удалит словарь и все помеченные для удаления сообщения

    else:
        print("Лист не найден")

    # Закрываем скачанный файл
    wb.close()
