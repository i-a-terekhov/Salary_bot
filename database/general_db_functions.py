import sqlite3
from sqlite3 import Connection, Error
from typing import Tuple

DATABASE_REG_NAME = 'database/bd.sql'


def open_database(db_name: str = DATABASE_REG_NAME) -> Connection:
    """Функция создает коннект к базе данных"""

    # Открываем или создаем базу данных
    connect = sqlite3.connect(db_name)
    return connect


def open_connection(table_name: str, name_of_columns: Tuple[str, ...], db_name: str = DATABASE_REG_NAME) -> Connection:
    """Функция открывает (или создает при отсутствии) таблицу с заданными столбцами"""

    # Открываем или создаем базу данных
    connect = open_database(db_name)
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
    """Функция подтверждает внесенные изменения и закрывает коннект"""

    connect.commit()
    connect.close()


def test_connection(table_name: str, required_columns: Tuple[str, ...]) -> bool:
    """Функция сравнивает имена столбцов таблицы с переданным кортежем имен"""

    print('Проверка подключения к БД: ', end='')
    try:
        connect = open_database()
        cursor = connect.cursor()

        # Проверяем существование таблицы и ее структуру
        cursor.execute(f'''
            PRAGMA table_info({table_name})
        ''')
        existing_columns = [col[1] for col in cursor.fetchall()]

        if set(existing_columns) != required_columns:
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


def display_all_data_from_table(table_name: str) -> None:
    """Функция выводит на печать все данные из таблицы"""

    connect = open_database()
    cursor = connect.cursor()

    # Выбираем все строки из таблицы users
    select_all_query = f'SELECT * FROM {table_name}'
    cursor.execute(select_all_query)

    # Получаем имена столбцов
    column_names = [col[0] for col in cursor.description]

    # Получаем все данные
    all_data = cursor.fetchall()

    if not all_data:
        print("В таблице нет данных.")
    else:
        print(column_names)
        for row in all_data:
            print(row)
    connect.close()


def update_data_in_column(
        table_name: str, base_column_name: str, base_column_value: str, target_column_name: str, new_value: str
) -> None:
    """Функция обновляет значение столбца target_column_name
    для заданного base_column_value в столбце base_column_name"""

    connect = open_database()
    cursor = connect.cursor()

    update_query = f'UPDATE {table_name} SET {target_column_name} = ? WHERE {base_column_name} = ?'
    cursor.execute(update_query, (new_value, base_column_value))
    print(f"Для столбца значения {base_column_value} в столбце {base_column_name} "
          f"обновлено значение в столбце {target_column_name} на {new_value}")

    close_connection(connect=connect)


def get_data_from_column(
        table_name: str, base_column_name: str, base_column_value: str, target_column_name: str
) -> list:
    """Функция возвращает значения из столбца target_column_name
    для для заданного base_column_value в столбце base_column_name
    (может быт несколько значений, если значение base_column_value не уникально"""

    connect = open_database()
    cursor = connect.cursor()

    # Формируем SQL-запрос для выбора данных из указанного столбца
    select_query = f"SELECT {target_column_name} FROM {table_name} WHERE {base_column_name} = ?"
    cursor.execute(select_query, (base_column_value,))

    # Извлекаем результат запроса
    results = cursor.fetchall()
    connect.close()

    # Если результат есть, возвращаем лист со значениями столбца, иначе возвращаем пустой список
    return [result[0] for result in results] if results else []
