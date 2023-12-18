import sqlite3
from sqlite3 import Connection, Error
from typing import Tuple

DATABASE_REG_NAME = 'database/bd.sql'


def open_connection(table_name: str, name_of_columns: Tuple[str, ...], db_name: str = DATABASE_REG_NAME) -> Connection:
    # Открываем или создаем базу данных
    connect = sqlite3.connect(db_name)
    cursor = connect.cursor()

    # Формируем строку с именами столбцов
    columns_str = ', '.join([f"{column} TEXT" for column in name_of_columns])

    # Создаем таблицу с динамически формированными столбцами
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS {table_name} (
            {columns_str}
        )
    ''')
    return connect


def close_connection(connect: Connection) -> None:
    connect.commit()
    connect.close()


def test_connection(table_name: str, required_columns: Tuple[str, ...]) -> bool:
    print('Проверка подключения к БД: ', end='')
    try:
        connect = open_connection(table_name=table_name, name_of_columns=required_columns)
        cursor = connect.cursor()

        # Проверяем существование таблицы и ее структуру
        cursor.execute(f'''
            PRAGMA table_info({table_name})
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
