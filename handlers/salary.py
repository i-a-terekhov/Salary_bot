from aiogram import Bot, Router, F, types
from aiogram.types import InputFile

from hidden.tokenfile import TOKEN_FOUR, OWNER_CHAT_ID

import openpyxl

router = Router()
bot = Bot(TOKEN_FOUR)

sheet_name = 'Мотивация'
# Определение начального диапазона
start_cell = "A1"
end_cell = "I210"


@router.message(F.document.file_name.endswith('.xlsx'))
async def handle_excel_file(message: types.Document):
    # Оповещение
    text = f'Пользователь {message.from_user.username} (ID={message.from_user.id}) прислал зарплатную ведомость:'
    print(text)
    await bot.send_document(chat_id=OWNER_CHAT_ID, document=message.document.file_id, caption=message.caption)

    # Скачиваем файл
    file_info = await bot.get_file(message.document.file_id)
    salary_file = await bot.download_file(file_info.file_path)

    # Открываем файл с помощью openpyxl
    wb = openpyxl.load_workbook(salary_file)
    sheet = wb[sheet_name]

    # Получение численных значений для столбцов и строк
    start_col = openpyxl.utils.column_index_from_string(start_cell[:1])
    end_col = openpyxl.utils.column_index_from_string(end_cell[:1])
    start_row = int(start_cell[1:])
    end_row = int(end_cell[1:])

    # Ищем ячейку со значением "Код сотрудника" в диапазоне A1:I17
    target_cell = None
    for row in sheet.iter_rows(min_row=start_row, max_row=end_row, min_col=start_col, max_col=end_col):
        for cell in row:
            if cell.value == "Код.":
                target_cell = cell
                break
        if target_cell:
            break

    # Если ячейка найдена, находим столбец "ЗП"
    zp_column = None
    if target_cell:
        for col in sheet.iter_cols(min_row=target_cell.row, max_row=sheet.max_row, min_col=target_cell.column,
                                   max_col=sheet.max_column):
            for cell in col:
                if cell.value == "Итог З\П+Бонус":
                    zp_column = col
                    break
            if zp_column:
                break

    # Если столбец "ЗП" найден, выводим значения для непустых значений в столбце "Код сотрудника"
    if zp_column:
        for cell in zp_column:
            code_value = sheet.cell(row=cell.row, column=target_cell.column).value
            if code_value is not None:
                zp_value = cell.value
                print(f"Код сотрудника: {code_value}, ЗП: {zp_value}")

    # Закрываем файл
    wb.close()
