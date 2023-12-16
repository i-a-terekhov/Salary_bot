import sqlite3
from sqlite3 import Connection, Error
from typing import List, Tuple

DATABASE_REG_NAME = 'database/bd.sql'
TABLE_NAME = 'users'
SALARY_TABLE = ('employee_code', 'secret_salary_code', 'author_of_entry', '')


def open_connection(db_name: str = DATABASE_REG_NAME, name_of_columns: Tuple[str] = SALARY_TABLE) -> Connection:
    # Открываем или создаем базу данных
    connect = sqlite3.connect(db_name)
    cursor = connect.cursor()

    # Формируем строку с именами столбцов
    columns_str = ', '.join([f"{column} TEXT" for column in name_of_columns])

    # Создаем таблицу с динамически формированными столбцами
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS users (
            {columns_str}
        )
    ''')
    return connect

# SALARY_TABLE = ("Дата табеля", "author_of_entry", "доступно руководителю", "попыток ввода пароля",
#                 "доступно сотруднику", 'secret_employee_code', 'employee_code', "Должность",
# "Ф.И.О.",
# "Итог З/П",  # Оклад
# "Итог мотивация",  # Премия
# "Итог З\П+Бонус",  # Всего
# "Премия(компенсация отпуска)",
# "Вычеты ОС(форма/прочее)",
# "Вычеты ОС(Инвентаризация)",
# 'Вычеты-штрафы',
# 'Факт часы',
# 'Кол-во ошибок (примечание)',
# 'Сумма ошибки',
# 'Единый коэфф.',
# 'Дополнительные работы Н/Ч',
# 'Выдача ',
# 'Доставки(Подготовка отгрузок)',
# 'Приемка',
# 'Размещение',
# 'Объем М3 кросс.',
# 'Сборка отгрузок')


SALARY_TABLE = ('Report_card_date', 'author_of_entry', 'available_to_supervisor', 'password_attempts',
                'available_to_employee', 'secret_employee_code', 'employee_code', 'Position', 'Full_name',
                'Salary_total', 'Total_motivation', 'Salary_total_plus_Bonus', 'Bonus_(vacation_compensation)',
                'Deductions_of_fixed_assets_(form/other)', 'OS_Deductions_(Inventory)', 'Deductions-penalties',
                'Actual_hours_worked', 'Number_of_errors', 'Error_amount', 'Single_output_coefficient',
                'Additional_work', 'Points_of_given_out', 'Delivery_Points', 'Acceptance_Points',
                'Placement_Points', 'Volume_M3_cross', 'Shipment_Assembly_Points')
