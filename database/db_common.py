import sqlite3
from sqlite3 import Connection, Error
from typing import Tuple

from database.general_db_functions import open_connection, close_connection

TABLE_NAME = 'users'
REGISTRATION_TABLE = ('telegram_id', 'telegram_username', 'state_in_bot',
                      'employee_code', 'secret_employee_code', 'registration_attempts')


def insert_user_to_database(reg_table: Tuple[str, ...] = REGISTRATION_TABLE) -> bool:
    """"
    :param reg_table: Кортеж, содержащий названия столбцов для вставки. Базовые столбцы:
    'telegram_id',
    'telegram_username',
    'state_in_bot',
    'employee_code',
    'secret_employee_code'
    'registration_attempts')
    """
    telegram_id, telegram_username, state_in_bot, employee_code, secret_employee_code, registration_attempts = reg_table
    connect = open_connection(table_name=TABLE_NAME, name_of_columns=REGISTRATION_TABLE)
    cursor = connect.cursor()

    # Проверяем наличие данных для указанного telegram_id
    select_query = 'SELECT * FROM users WHERE telegram_id = ?'
    cursor.execute(select_query, (telegram_id,))
    existing_data = cursor.fetchone()

    if existing_data:
        # Если данный юзер уже существует, ничего вставлять не надо:
        print(f"Юзер {telegram_id}: данные уже есть БД")
        successful_insert = False
    else:
        # Если данного юзера нет, вставляем новую запись
        insert_query = 'INSERT INTO users (telegram_id, telegram_username, state_in_bot, employee_code, ' \
                       'secret_employee_code, registration_attempts) VALUES (?, ?, ?, ?, ?, ?) '
        cursor.execute(insert_query,
                       (telegram_id, telegram_username, state_in_bot,
                        employee_code, secret_employee_code, registration_attempts))
        print(f"Юзер {telegram_id}: данные успешно записаны в БД")
        display_all_data()
        successful_insert = True

    # Фиксируем изменения и закрываем соединение
    close_connection(connect=connect)
    return successful_insert


def update_data_in_column(telegram_id: str, column: str, value: str) -> None:
    connect = open_connection()
    cursor = connect.cursor()

    update_query = f'UPDATE users SET {column} = ? WHERE telegram_id = ?'
    cursor.execute(update_query, (value, telegram_id))
    print(f"Для юзера {telegram_id} обновлено значение в столбце {column} на {value}")

    close_connection(connect=connect)


def display_all_data() -> None:
    connect = open_connection(table_name=TABLE_NAME, name_of_columns=REGISTRATION_TABLE)
    cursor = connect.cursor()

    # Выбираем все строки из таблицы users
    select_all_query = 'SELECT * FROM users'
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


def get_data_from_column(telegram_id: str, column: str) -> str:
    connect = open_connection(table_name=TABLE_NAME, name_of_columns=REGISTRATION_TABLE)
    cursor = connect.cursor()

    # Формируем SQL-запрос для выбора данных из указанного столбца
    select_query = f"SELECT {column} FROM users WHERE telegram_id = ?"
    cursor.execute(select_query, (telegram_id,))

    # Извлекаем результат запроса
    result = cursor.fetchone()
    connect.close()

    # Если результат есть, возвращаем значение столбца, иначе возвращаем пустую строку
    return result[0] if result else ""


def get_user_state_from_db(telegram_id: str) -> str | bool:
    target_column = 'state_in_bot'
    value = get_data_from_column(telegram_id=telegram_id, column=target_column)
    if value != "":
        return value
    else:
        return False


def save_user_state_to_db(telegram_id: str, new_state: str) -> None:
    target_column = 'state_in_bot'
    update_data_in_column(telegram_id=telegram_id, column=target_column, value=new_state)


