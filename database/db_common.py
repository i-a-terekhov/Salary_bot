import sqlite3
from sqlite3 import Connection
from typing import List

DATABASE_NAME = 'database/bd.sql'


# def open_connection(db_name: str = DATABASE_NAME) -> Connection:
#     # Открываем Создаем базу данных, если она не существует
#     connect = sqlite3.connect(db_name)
#     cursor = connect.cursor()
#     cursor.execute('''
#         CREATE TABLE IF NOT EXISTS users (
#             user_id INTEGER PRIMARY KEY,
#             state TEXT,
#             employee_data TEXT
#         )
#     ''')
#     return connect


def open_connection(db_name: str = DATABASE_NAME, table_name: str = "users", columns: List[str] = None) -> Connection:
    # Открываем или создаем базу данных
    connect = sqlite3.connect(db_name)
    cursor = connect.cursor()

    # Проверяем существование таблицы
    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
    table_exists = cursor.fetchone()

    if not table_exists:
        # Если таблицы нет, создаем ее с заданными столбцами
        cursor.execute(f'''
            CREATE TABLE {table_name} (
                user_id INTEGER PRIMARY KEY,
                state TEXT,
                employee_data TEXT
            )
        ''')
    else:
        # Если таблица существует, добавляем отсутствующие столбцы
        if columns:
            for column in columns:
                cursor.execute(f"PRAGMA table_info({table_name})")
                existing_columns = [col[1] for col in cursor.fetchall()]

                if column not in existing_columns:
                    cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column} TEXT")

            # Получаем текущий порядок столбцов
            cursor.execute(f"PRAGMA table_info({table_name})")
            current_columns = [col[1] for col in cursor.fetchall()]
            print(f'Текущий порядок столбцов {current_columns}')

            # Переупорядочиваем столбцы в нужном порядке
            select_columns = ", ".join(columns)
            cursor.execute(f"CREATE TABLE {table_name}_backup AS SELECT {select_columns} FROM {table_name}")
            cursor.execute(f"DROP TABLE {table_name}")
            cursor.execute(f"CREATE TABLE {table_name} AS SELECT * FROM {table_name}_backup")
            cursor.execute(f"DROP TABLE {table_name}_backup")

    return connect


def close_connection(connect: Connection) -> None:
    connect.commit()
    connect.close()


def one_time_connection(db_name: str = DATABASE_NAME, table_name: str = "users", columns: List[str] = None) -> None:
    close_connection(open_connection(db_name=db_name, table_name=table_name, columns=columns))
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
    connect.close()


def add_column(column_name: str, data_type: str, db_name: str = DATABASE_NAME):
    connection = open_connection(db_name=db_name)
    cursor = connection.cursor()
    try:
        cursor.execute(f'ALTER TABLE users ADD COLUMN {column_name} {data_type}')
        print(f"Поле {column_name} успешно добавлено.")
    except sqlite3.OperationalError as e:
        print(f"Ошибка при добавлении поля {column_name}: {e}")
    close_connection(connect=connection)


def drop_columns(*column_names: str, db_name: str = DATABASE_NAME) -> None:
    # Открываем соединение с базой данных
    connection = open_connection(db_name=db_name)
    cursor = connection.cursor()

    try:
        # Проверяем существование столбцов
        cursor.execute(f"PRAGMA table_info(users);")
        columns_info = cursor.fetchall()
        existing_columns = [column_info[1] for column_info in columns_info]

        for column_name in column_names:
            if column_name not in existing_columns:
                print(f"Столбец {column_name} не существует в таблице 'users'.")
                return

        # Формируем список столбцов для выбора в SELECT и для вставки в новую таблицу
        select_columns = ', '.join(existing_columns)
        insert_columns = ', '.join(existing_columns)
        for column_name in column_names:
            select_columns = select_columns.replace(f"{column_name}, ", "")
            insert_columns = insert_columns.replace(f"{column_name}, ", "")

        cursor.execute(f'PRAGMA foreign_keys=off;')
        # Отключает внешние ключи в базе данных. Внешние ключи связаны с целостностью данных и предотвращают
        # выполнение операций, которые могли бы привести к нарушению связей между таблицами. Однако при изменении
        # структуры таблицы, такой как удаление столбца, временное отключение внешних ключей может быть необходимым.

        cursor.execute(f'SAVEPOINT drop_column;')
        # Создает точку сохранения с именем "drop_column". Точка сохранения используется для того, чтобы можно
        # было откатить изменения в случае возникновения ошибки в ходе выполнения последующих операций.

        # TODO сравнить оба варианта:
        # cursor.execute(f'CREATE TABLE users_backup AS SELECT {select_columns} FROM users;')
        cursor.execute(f'CREATE TABLE users_backup AS SELECT {", ".join(column_names)} FROM users;')
        # Создает резервную копию таблицы "users" под именем "users_backup". В этой таблице сохраняются все данные
        # из оригинальной таблицы.

        cursor.execute(f'DROP TABLE users;')
        # Удаляет оригинальную таблицу "users". Это необратимая операция.

        # TODO сравнить оба варианта:
        # cursor.execute(f'CREATE TABLE users AS SELECT {insert_columns} FROM users_backup;')
        cursor.execute(f'CREATE TABLE users AS SELECT {", ".join(column_names)} FROM users_backup;')
        # Восстанавливает таблицу "users" из резервной копии "users_backup". Теперь таблица "users" снова существует,
        # но без удаленного столбца.

        cursor.execute(f'PRAGMA foreign_keys=on;')
        # Включает внешние ключи после выполнения изменений. Теперь база данных возвращает свою обычную
        # функциональность по обеспечению целостности данных.

        cursor.execute(f'RELEASE drop_column;')
        # Откатывает точку сохранения "drop_column". Если на этом этапе возникла ошибка, изменения, внесенные после
        # точки сохранения, откатываются.

        cursor.execute(f'DROP TABLE users_backup;')
        # Удаляет резервную копию "users_backup". После восстановления данных и отката точки сохранения резервная
        # копия больше не нужна.

        # Фиксируем изменения и закрываем соединение
        connection.commit()

        print(f"Столбцы {', '.join(column_names)} успешно удалены.")
    except Exception as e:
        # В случае ошибки откатываем транзакцию
        connection.rollback()
        print(f"Произошла ошибка при удалении столбцов {', '.join(column_names)}: {e}")
    finally:
        # Закрываем соединение
        close_connection(connect=connection)
