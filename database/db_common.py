import sqlite3
from sqlite3 import Connection

DATABASE_NAME = 'database/bd.sql'


def open_connection(db_name: str = DATABASE_NAME) -> Connection:
    # Открываем Создаем базу данных, если она не существует
    connect = sqlite3.connect(db_name)
    cursor = connect.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            state TEXT,
            employee_data TEXT
        )
    ''')
    return connect


def close_connection(connect: Connection) -> None:
    connect.commit()
    connect.close()


def one_time_connection(db_name: str = DATABASE_NAME) -> None:
    close_connection(open_connection(db_name=db_name))
    print('База существует')


def insert_data(user_id, state, employee_data, db_name: str = DATABASE_NAME) -> bool:
    # Создаем базу данных, если она не существует
    connection = open_connection(db_name=db_name)
    cursor = connection.cursor()

    # Проверяем наличие данных для указанного user_id
    select_query = 'SELECT * FROM users WHERE user_id = ?'
    cursor.execute(select_query, (user_id,))
    existing_data = cursor.fetchone()

    if existing_data:
        # Если данные уже существуют, запрашиваем у пользователя обновление
        update_option = input(f"Данные для user_id {user_id} уже существуют. Хотите обновить их? (y/n): ")
        if update_option.lower() == 'y':
            # Обновляем данные
            update_query = 'UPDATE users SET state = ?, employee_data = ? WHERE user_id = ?'
            cursor.execute(update_query, (state, employee_data, user_id))
            print(f"Данные для user_id {user_id} успешно обновлены.")
            successful_insert = True
        else:
            print(f"Ничего не вставлено для user_id {user_id}.")
            successful_insert = False
    else:
        # Данных нет, вставляем новую запись
        insert_query = 'INSERT INTO users (user_id, state, employee_data) VALUES (?, ?, ?)'
        cursor.execute(insert_query, (user_id, state, employee_data))
        print(f"Данные для user_id {user_id} успешно вставлены.")
        successful_insert = True

    # Фиксируем изменения и закрываем соединение
    close_connection(connect=connection)
    return successful_insert


def display_all_data(db_name: str = DATABASE_NAME) -> None:
    # Создаем базу данных, если она не существует
    connect = open_connection(db_name=db_name)
    cursor = connect.cursor()

    # Выбираем все строки из таблицы users
    select_all_query = 'SELECT * FROM users'
    cursor.execute(select_all_query)
    all_data = cursor.fetchall()

    if not all_data:
        print("В таблице нет данных.")
    else:
        for row in all_data:
            print(row)

    # Закрываем соединение
    connect.close()
