from aiogram import Bot, Router, F, types

from hidden.tokenfile import TOKEN_FOUR, OWNER_CHAT_ID

import openpyxl
from openpyxl import Workbook
from openpyxl import load_workbook

router = Router()
bot = Bot(TOKEN_FOUR)

# Для поиска нужного листа мотивации ищем на каждом листе в диапазоне А1:С3 значение:
try_sheet_factor = 'Мотивация по не  учетным данным'

# Определение начального диапазона целевого листа для поиска нужных столбцов (код сотрудника, ЗП, премия и пр.)
start_cell = "A1"
end_cell = "I210"

# Получение численных значений для столбцов и строк
start_col = openpyxl.utils.column_index_from_string(start_cell[:1])
end_col = openpyxl.utils.column_index_from_string(end_cell[:1])
start_row = int(start_cell[1:])
end_row = int(end_cell[1:])

base_cell = "Код."
dependent_cell_one = "Должность"
dependent_cell_two = "Ф.И.О."
dependent_cell_three = "Итог З/П"
dependent_cell_four = "Итог мотивация"
dependent_cell_five = "Итог З\П+Бонус"
dependent_cell_six = "Премия(компенсация отпуска)"
dependent_cell_seven = "Вычеты ОС(форма/прочее)"
dependent_cell_eight = "Вычеты ОС(Инвентаризация)"


async def search_salary_value(target_sheet, base_cell_name=base_cell):
    # Ищем базовую ячейку в диапазоне start_cell:end_cell
    target_cell = None
    for row in target_sheet.iter_rows(min_row=start_row, max_row=end_row, min_col=start_col, max_col=end_col):
        for cell in row:
            if cell.value == base_cell_name:
                target_cell = cell
                break
        if target_cell:
            break
    # Если базовая ячейка (шапка базового столбца) найдена, ищем целевые столбцы:
    if target_sheet:
        list_of_persons = []
        await find_it(target_cell, target_sheet, target_column_name=dependent_cell_two)


async def find_it(target_cell, target_sheet, target_column_name):
    # Ищем целевой столбец
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
            code_value = target_sheet.cell(row=cell.row, column=target_cell.column).value
            if code_value is not None:
                zp_value = cell.value
                print(f"Код сотрудника: {code_value}, ЗП: {zp_value}")


@router.message(F.document.file_name.endswith('.xlsx'))
async def handle_excel_file(message: types.Document):
    # Оповещение
    text = f'Пользователь {message.from_user.username} (ID={message.from_user.id}) прислал зарплатную ведомость:'
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
                    target_sheet = sheet
                    break
        if target_sheet:
            break

    if target_sheet:
        # Используем target_sheet для дальнейших действий
        print(f"Найден лист: {target_sheet.title}")

        await search_salary_value(target_sheet=target_sheet, base_cell_name=base_cell)

    else:
        print("Лист не найден")

    # Закрываем скачанный файл
    wb.close()

