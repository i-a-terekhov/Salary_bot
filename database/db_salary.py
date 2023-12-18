import sqlite3
from sqlite3 import Connection, Error
from typing import List, Tuple

DATABASE_REG_NAME = 'database/bd.sql'
TABLE_NAME = 'salary'
SALARY_TABLE = ('Report_card_date', 'Author_of_entry', 'Available_to_supervisor',
                # Дата табеля,      Руководитель,       Доступно руководителю,

                'Available_to_employee', 'Employee_code', 'Position', 'Full_name',
                # Доступно сотруднику,  Код сотрудника,   Должность,    Ф.И.О.,

                'Salary_total', 'Total_motivation', 'Salary_total_plus_Bonus', 'Bonus_vacation_compensation',
                # Итог З/П,     Итог мотивация,     Итог З\П+Бонус,             Премия(компенсация отпуска),

                'Deductions_of_fixed_assets_form_other', 'OS_Deductions_Inventory', 'Deductions_penalties',
                # Вычеты ОС(форма/прочее),                  Вычеты ОС(Инвентаризация),      Вычеты-штрафы

                'Actual_hours_worked', 'Number_of_errors', 'Error_amount', 'Single_output_coefficient',
                # Факт часы,        Кол-во ошибок (примечание), Сумма ошибки,   Единый коэфф.,

                'Additional_work', 'Points_of_given_out', 'Delivery_Points', 'Acceptance_Points',
                # Дополнительные работы Н/Ч, Выдача,    Доставки(Подготовка отгрузок), Приемка,

                'Placement_Points', 'Volume_M3_cross', 'Shipment_Assembly_Points'
                # Размещение,           Объем М3 кросс.,    Сборка отгрузок
                )

TRANSLATE_DICT = {
    'Код.': 'Employee_code',
    'Должность': 'Position',
    'Ф.И.О.': 'Full_name',
    'Итог З/П': 'Salary_total',
    'Итог мотивация': 'Total_motivation',
    'Итог З\П+Бонус': 'Salary_total_plus_Bonus',
    'Премия(компенсация отпуска)': 'Bonus_vacation_compensation',
    'Вычеты ОС(форма/прочее)': 'Deductions_of_fixed_assets_form_other',
    'Вычеты ОС(Инвентаризация)': 'OS_Deductions_Inventory',
    'Вычеты-штрафы': 'Deductions_penalties',
    'Факт часы': 'Actual_hours_worked',
    'Кол-во ошибок (примечание)': 'Number_of_errors',
    'Сумма ошибки': 'Error_amount',
    'Единый коэфф.': 'Single_output_coefficient',
    'Дополнительные работы Н/Ч': 'Additional_work',
    'Выдача ': 'Points_of_given_out',
    'Доставки(Подготовка отгрузок)': 'Delivery_Points',
    'Приемка': 'Acceptance_Points',
    'Размещение': 'Placement_Points',
    'Объем М3 кросс.': 'Volume_M3_cross',
    'Сборка отгрузок': 'Shipment_Assembly_Points'
}


def open_connection(db_name: str = DATABASE_REG_NAME, name_of_columns: Tuple[str] = SALARY_TABLE) -> Connection:
    # Открываем или создаем базу данных
    connect = sqlite3.connect(db_name)
    cursor = connect.cursor()

    # Формируем строку с именами столбцов
    columns_str = ', '.join([f"{column} TEXT" for column in name_of_columns])

    # Создаем таблицу с динамически формированными столбцами
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            {columns_str}
        )
    ''')
    return connect


def close_connection(connect: Connection) -> None:
    connect.commit()
    connect.close()


def test_connection(required_columns: Tuple[str] = SALARY_TABLE) -> bool:
    print('Проверка подключения к БД: ', end='')
    try:
        connect = open_connection()
        cursor = connect.cursor()

        # Проверяем существование таблицы и ее структуру
        cursor.execute(f'''
            PRAGMA table_info({TABLE_NAME})
        ''')
        existing_columns = [col[1] for col in cursor.fetchall()]

        if set(existing_columns) != set(required_columns):
            print("Структура таблицы не соответствует требуемой")
            print(f'existing_columns: {existing_columns}')
            print(f'required_columns: {required_columns}')
            connect.close()
            return False
        connect.close()
        print("ОК")
        return True

    except Error as e:
        print(f"Error: {e}")
        return False


def insert_dict_of_persons_to_database(dict_of_persons: dict, dict_of_filling: dict) -> bool:
    """Функция принимает два словаря: dict_of_persons с данными по сотрудникам и dict_of_filling с данными по заливке"""
    connect = open_connection()
    cursor = connect.cursor()

    try:
        for user_id in dict_of_persons:
            # Вставляем новую запись
            filling_str = ', '.join(dict_of_filling.keys())
            filling_val = ', '.join(['?' for _ in dict_of_filling])

            columns_str = ', '.join(dict_of_persons[user_id].keys()) + ', ' + filling_str
            values_str = ', '.join(['?' for _ in dict_of_persons[user_id]]) + ', ' + filling_val
            for ru_name in TRANSLATE_DICT:
                # print(f'Ищем {ru_name} в строке {columns_str}')
                columns_str = columns_str.replace(ru_name, TRANSLATE_DICT[ru_name])

            print('-' * 100)
            print(columns_str)
            print(values_str)
            print('-' * 100)

            insert_query = f'INSERT INTO {TABLE_NAME} ({columns_str}) VALUES ({values_str})'

            values_tuple = tuple(str(value) for value in dict_of_persons[user_id].values())
            values_tuple += tuple(dict_of_filling.values())
            cursor.execute(insert_query, values_tuple)
            # print(f'Данные юзера {user_id} занесены в БД')
            connect.commit()
        print(f"Все данные из словаря dict_of_persons успешно записаны в БД")
        # display_all_data()
        successful_insert = True
    except Exception as e:
        print(f"Ошибка при вставке данных в БД: {e}")
        successful_insert = False

    # Фиксируем изменения и закрываем соединение
    close_connection(connect=connect)
    return successful_insert


def update_data_in_column(telegram_id: str, column: str, value: str) -> None:
    connect = open_connection()
    cursor = connect.cursor()

    update_query = f'UPDATE {TABLE_NAME} SET {column} = ? WHERE telegram_id = ?'
    cursor.execute(update_query, (value, telegram_id))
    print(f"Для юзера {telegram_id} обновлено значение в столбце {column} на {value}")

    close_connection(connect=connect)


def display_all_data() -> None:
    connect = open_connection()
    cursor = connect.cursor()

    # Выбираем все строки из таблицы salary
    select_all_query = f'SELECT * FROM {TABLE_NAME}'
    cursor.execute(select_all_query)

    # Получаем имена столбцов
    column_names = [col[0] for col in cursor.description]

    all_data = cursor.fetchall()

    if not all_data:
        print("В таблице нет данных.")
    else:
        print(column_names)
        for row in all_data:
            print(row)
    connect.close()
