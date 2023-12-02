import sqlite3
from sqlite3 import Connection, Error
from typing import List, Tuple

DATABASE_REG_NAME = 'database/bd.sql'
TABLE_NAME = 'users'
REGISTRATION_TABLE = ('telegram_id', 'telegram_username', 'state_in_bot', 'employee_code', 'secret_employee_code')


def open_connection(db_name: str = DATABASE_REG_NAME, name_of_columns: Tuple[str] = REGISTRATION_TABLE) -> Connection:
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


def close_connection(connect: Connection) -> None:
    connect.commit()
    connect.close()


def test_connection(required_columns: Tuple[str] = REGISTRATION_TABLE) -> bool:
    print('Проверка подключения к БД: ', end='')
    try:
        connect = open_connection()
        cursor = connect.cursor()

        # Проверяем существование таблицы и ее структуру
        cursor.execute('''
            PRAGMA table_info(users)
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


def insert_data(reg_table: Tuple[str, str, str, str, str] = REGISTRATION_TABLE) -> bool:
    """"
    :param reg_table: Кортеж, содержащий названия столбцов для вставки. Базовые столбцы:
    'telegram_id',
    'telegram_username',
    'state_in_bot',
    'employee_code',
    'secret_employee_code'
    """
    telegram_id, telegram_username, state_in_bot, employee_code, secret_employee_code = reg_table
    connect = open_connection()
    cursor = connect.cursor()

    # Проверяем наличие данных для указанного telegram_id
    select_query = 'SELECT * FROM users WHERE telegram_id = ?'
    cursor.execute(select_query, (telegram_id,))
    existing_data = cursor.fetchone()

    if existing_data:
        # TODO в продакте не будет подтверждения перезаписи, т.е. нужна точка выхода, если запись уже есть:
        # Если данные уже существуют, запрашиваем у пользователя обновление
        # --------------------------------------------------------------------------------------------------------------
        # update_option = input(
        #     f"Данные для {telegram_username} {telegram_id} уже существуют. Хотите обновить их? (y/n): ")
        # if update_option.lower() == 'y':
        # --------------------------------------------------------------------------------------------------------------
        if 1 == 1:
            # Обновляем данные
            update_query = 'UPDATE users SET telegram_username = ?, state_in_bot = ?, employee_code = ?, ' \
                           'secret_employee_code = ? WHERE telegram_id = ? '
            cursor.execute(update_query,
                           (telegram_id, telegram_username, state_in_bot, employee_code, secret_employee_code,))
            print(f"Данные для {telegram_username} {telegram_id} успешно обновлены.")
            successful_insert = True
        # --------------------------------------------------------------------------------------------------------------
        # else:
        #     print(f"Ничего не вставлено для {telegram_username} {telegram_id}.")
        #     successful_insert = False
        # --------------------------------------------------------------------------------------------------------------
    else:
        # Данных нет, вставляем новую запись
        insert_query = 'INSERT INTO users (telegram_id, telegram_username, state_in_bot, employee_code, ' \
                       'secret_employee_code) VALUES (?, ?, ?, ?, ?) '
        cursor.execute(insert_query,
                       (telegram_id, telegram_username, state_in_bot, employee_code, secret_employee_code))
        print(f"Данные для {telegram_username} {telegram_id} успешно вставлены.")
        successful_insert = True

    # Фиксируем изменения и закрываем соединение
    close_connection(connect=connect)
    return successful_insert


def insert_data_in_column(telegram_id: str, column: str, value: str) -> None:
    connect = open_connection()
    cursor = connect.cursor()

    update_query = f'UPDATE users SET {column} = ? WHERE telegram_id = ?'
    cursor.execute(update_query, (value, telegram_id))
    print(f"Данные для {telegram_id} обновлено в столбце {column}")

    close_connection(connect=connect)


def display_all_data() -> None:
    connect = open_connection()
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
    pass
    connect = open_connection()
    cursor = connect.cursor()


