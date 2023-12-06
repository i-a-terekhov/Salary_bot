from aiogram import Bot, Router, F, types

from hidden.tokenfile import TOKEN_FOUR, OWNER_CHAT_ID

import openpyxl
from openpyxl import Workbook
from openpyxl import load_workbook

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
target_column_one = "Должность"
target_column_two = "Ф.И.О."
target_column_three = "Итог З/П"
target_column_four = "Итог мотивация"
target_column_five = "Итог З\П+Бонус"
target_column_six = "Премия(компенсация отпуска)"
target_column_seven = "Вычеты ОС(форма/прочее)"
target_column_eight = "Вычеты ОС(Инвентаризация)"
target_columns = [target_column_one, target_column_two, target_column_three,
                  target_column_four, target_column_five, target_column_six,
                  target_column_seven, target_column_eight]


def search_salary_value(target_sheet, base_cell_name=base_column) -> dict:
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
                target_cell=head_of_base_column, target_sheet=target_sheet,
                target_column_name=target, dict_of_persons=dict_of_persons
            )
        return dict_of_persons


def forming_small_results_of_table(dict_of_persons: dict) -> str:
    # Формируем краткий текст для подтверждения заливки руководителем.
    # В данном случае, в формате: "Фамилия: итог ЗП"
    text = ''
    for person_no in dict_of_persons:

        surname = str(dict_of_persons[person_no]["Ф.И.О."]).split(' ')[0]
        if len(surname) < 15:
            extra_space = 15 - len(surname)
            surname += ' ' * extra_space

        summ = dict_of_persons[person_no][target_column_five]

        text += f'{surname}{summ:_} руб.\n'
    print(text)
    return text


def forming_results_for_one_employee(dict_of_persons: dict) -> str:
    # TODO функция, формирующая один квиток
    pass


def search_values_of_one_target_column(target_cell, target_sheet, target_column_name, dict_of_persons) -> None:
    # Ищем целевой столбец.
    # Например, если базовый - "ID юзера", то целевым может быть - "Показатель" юзера по какому-то критерию
    target_column = None
    if target_cell:
        for col in target_sheet.iter_cols(min_row=target_cell.row, max_row=target_sheet.max_row,
                                          min_col=target_cell.column, max_col=target_sheet.max_column):
            for cell in col:
                if cell.value == target_column_name:
                    target_column = col
                    break
            if target_column:
                break
    # Если целевой столбец найден, выводим значения для непустых значений в базовом столбце
    if target_column:
        for cell in target_column:
            base_colum_value = target_sheet.cell(row=cell.row, column=target_cell.column).value
            # Так же проверяем первые 4 символа (являются ли числами), чтобы отбросить строки-разделители
            if len(str(base_colum_value)) > 4 and str(base_colum_value)[:4].isdigit():
                # Добавляем значения в словарь
                if base_colum_value not in dict_of_persons:
                    dict_of_persons[base_colum_value] = {}
                dict_of_persons[base_colum_value][target_column_name] = cell.value


# Когда руководитель подтверждает суммы, бот просит его придумать пароль для этой конкретной заливки
#TODO функция, проверяющая "секретный зарплатный код" для конкретной заливки

# Когда ЗП-пароль установлен, данные перемещаются в БД, а руководителю высылаются секретные коды сотрудников
#TODO функция, высылающая руководителю файл(?) с секретными кодами сотрудников после заливки
#TODO функция, формирующая записи в зарплатной таблице (с секртеным кодом, "попыток ввода", датой заливки, "доступом" и пр. доп. столбцами)

#TODO добавить удаление сообщения с файлом!!!

@router.message(F.document.file_name.endswith('.xlsx'), Registration.employee_is_registered)
async def handle_excel_file(message: types.Document):
    # Оповещение
    text = f'Юзер {message.from_user.id} прислал зарплатную ведомость'
    print(text)
    await bot.send_document(chat_id=OWNER_CHAT_ID, document=message.document.file_id, caption=message.caption)

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
        dict_of_persons = search_salary_value(target_sheet=target_sheet, base_cell_name=base_column)
        text = forming_small_results_of_table(dict_of_persons=dict_of_persons)
        await bot.send_message(chat_id=message.from_user.id, text='В Вашем файле я обнаружил зарплатную таблицу. '
                                                                  'Вот краткие итоги, чтобы проверить суммы:')
        await bot.send_message(chat_id=message.from_user.id, text=text)

        await bot.send_message(chat_id=message.from_user.id, text='Готовы разослать эти данные?')
        #TODO здесь должна быть кнопки "Да, выслать данные" и "Посмотреть как будет выглядеть квиток"



    else:
        print("Лист не найден")

    # Закрываем скачанный файл
    wb.close()

