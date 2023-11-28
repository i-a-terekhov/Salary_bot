import sqlite3

DATABASE_NAME = 'bd.sql'


def display_all_data():
    # Создаем базу данных, если она не существует
    connect = sqlite3.connect(DATABASE_NAME)
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


# Пример использования
display_all_data()
