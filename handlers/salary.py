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
target_column_15 = 'Выдача'
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
                base_column_head=head_of_base_column, target_sheet=target_sheet,
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

        summ = dict_of_persons[person_no][target_column_05]

        text += f'{surname}{summ:_} руб.\n'
    print(text)
    return text


def forming_results_for_one_employee(dict_of_persons: dict) -> str:
    # TODO функция, формирующая один квиток
    pass


def search_values_of_one_target_column(base_column_head, target_sheet, target_column_name, dict_of_persons) -> None:
    # Ищем целевой столбец.
    # Например, если базовый - "ID юзера", то целевым может быть - "Показатель" юзера по какому-то критерию
    target_column = None
    if base_column_head:
        #TODO необходимо внести изменения в зоны для поиска целевых столбцов, т.к. наименования столбцов повторяются
        # а столбцы с нужными данными находятся не в начале:

        # for col in target_sheet.iter_cols(min_row=base_column_head.row, max_row=target_sheet.max_row,
        #                                   min_col=base_column_head.column, max_col=target_sheet.max_column):

        # Проходим по ряду, в котором находятся истинные заголовки:
        for col in target_sheet.iter_cols(min_row=39, max_row=39,
                                          min_col=base_column_head.column, max_col=target_sheet.max_column):
            # Действия с col
            for cell in col:
                # Если значение ячейки совпадает с именем столбца, требующего сдвига, считаем det = 1, иначе det = 0:

                if cell.value == target_column_name:
                    det = 1
                else:
                    det = 0

                # Проходим по строкам столбца col
                for cell_in_targ_col in target_sheet.iter_cols(min_row=base_column_head.row,
                                                               max_row=target_sheet.max_row,
                                                               min_col=col[0].column + amount_of_indentation * det,
                                                               max_col=col[0].column + amount_of_indentation * det):
                    target_column = cell_in_targ_col
                # print(target_column)
                # print('---')
                break
            if target_column:
                break
    # Если целевой столбец найден, выводим значения для непустых значений в базовом столбце
    if target_column:
        print(target_column)
        print('----' * 20)

        # # Если целевой столбец из числа требующих сдвига, делаем сдвиг:
        # if target_column[0].column in offset_columns:
        #     print('old', target_column_name)
        #     # Используем свойство column для получения номера столбца, добавляем смещение и создаем новый объект столбца
        #     new_column_index = target_column[0].column + amount_of_indentation
        #     target_column = target_sheet[new_column_index]

        for cell in target_column:
            base_colum_value = target_sheet.cell(row=cell.row, column=base_column_head.column).value
            # Так же проверяем первые 4 символа (являются ли числами), чтобы отбросить строки-разделители
            if len(str(base_colum_value)) > 4 and str(base_colum_value)[:4].isdigit():
                # Добавляем значения в словарь
                if base_colum_value not in dict_of_persons:
                    dict_of_persons[base_colum_value] = {}
                dict_of_persons[base_colum_value][target_column_name] = cell.value


# Когда руководитель подтверждает суммы, бот просит его придумать пароль для этой конкретной заливки
# TODO функция, проверяющая "секретный зарплатный код" для конкретной заливки

# Когда ЗП-пароль установлен, данные перемещаются в БД, а руководителю высылаются секретные коды сотрудников
# TODO функция, высылающая руководителю файл(?) с секретными кодами сотрудников после заливки
# TODO функция, формирующая записи в зарплатной таблице (с секртеным кодом, "попыток ввода", датой заливки, "доступом" и пр. доп. столбцами)

# TODO добавить удаление сообщения с файлом!!!

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
        if not text:
            text = 'Ничего не найдено'
        await bot.send_message(chat_id=message.from_user.id, text='В Вашем файле я обнаружил зарплатную таблицу. '
                                                                  'Вот краткие итоги, чтобы проверить суммы:')
        await bot.send_message(chat_id=message.from_user.id, text=text)

        await bot.send_message(chat_id=message.from_user.id, text='Готовы разослать эти данные?')
        print(dict_of_persons)
        # TODO здесь должна быть кнопки "Да, выслать данные" и "Посмотреть как будет выглядеть квиток"

    else:
        print("Лист не найден")

    # Закрываем скачанный файл
    wb.close()
