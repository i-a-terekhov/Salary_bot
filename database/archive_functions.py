import sqlite3
from typing import List

from db_common import open_connection, close_connection, TABLE_NAME


def repair_table(table_name: str = TABLE_NAME, columns: List[str] = None) -> None:
    # Открываем или создаем базу данных
    connect = open_connection()
    cursor = connect.cursor()

    # Проверяем существование таблицы
    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
    table_exists = cursor.fetchone()

    if not table_exists:
        # Если таблицы нет, создаем ее с заданными столбцами
        cursor.execute(f'''
            CREATE TABLE {table_name} (
                telegram_id INTEGER PRIMARY KEY,
                state_in_bot TEXT,
                employee_code TEXT
            )
        ''')
    else:
        # Если таблица существует, добавляем отсутствующие столбцы
        if columns:
            for column in columns:
                cursor.execute(f"PRAGMA table_info({table_name})")
                existing_columns = [col[1] for col in cursor.fetchall()]

                if column not in existing_columns:
                    print(f'В таблице {table_name} отсутствовал столбец {column}')
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
    connect.commit()
    connect.close()


def add_column(column_name: str, data_type: str):
    connect = open_connection()
    cursor = connect.cursor()
    try:
        cursor.execute(f'ALTER TABLE users ADD COLUMN {column_name} {data_type}')
        print(f"Поле {column_name} успешно добавлено.")
    except sqlite3.OperationalError as e:
        print(f"Ошибка при добавлении поля {column_name}: {e}")
    close_connection(connect=connect)


def drop_columns(*column_names: str) -> None:
    connect = open_connection()
    cursor = connect.cursor()

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
        for column_name in column_names:
            select_columns = select_columns.replace(f"{column_name}, ", "")

        cursor.execute(f'PRAGMA foreign_keys=off;')
        # Отключает внешние ключи в базе данных. Внешние ключи связаны с целостностью данных и предотвращают
        # выполнение операций, которые могли бы привести к нарушению связей между таблицами. Однако при изменении
        # структуры таблицы, такой как удаление столбца, временное отключение внешних ключей может быть необходимым.

        cursor.execute(f'SAVEPOINT drop_column;')
        # Создает точку сохранения с именем "drop_column". Точка сохранения используется для того, чтобы можно
        # было откатить изменения в случае возникновения ошибки в ходе выполнения последующих операций.

        cursor.execute(f'CREATE TABLE users_backup AS SELECT {select_columns} FROM users;')
        # Создает резервную копию таблицы "users" под именем "users_backup". В этой таблице сохраняются все данные
        # из оригинальной таблицы.

        cursor.execute(f'DROP TABLE users;')
        # Удаляет оригинальную таблицу "users". Это необратимая операция.

        cursor.execute(f'CREATE TABLE users AS SELECT {select_columns} FROM users_backup;')
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
        connect.commit()

        print(f"Столбцы {', '.join(column_names)} успешно удалены.")
    except Exception as e:
        # В случае ошибки откатываем транзакцию
        connect.rollback()
        print(f"Произошла ошибка при удалении столбцов {', '.join(column_names)}: {e}")
    finally:
        # Закрываем соединение
        close_connection(connect=connect)


def delete_empty_rows(table_name: str = TABLE_NAME):
    connect = open_connection()
    cursor = connect.cursor()

    # Получаем имена столбцов в таблице
    cursor.execute(f"PRAGMA table_info({table_name})")
    column_names = [col[1] for col in cursor.fetchall() if col[1] != 'telegram_id']

    # Формируем строку с условием для каждого столбца, проверяя на NULL
    conditions = " AND ".join([f"{column} IS NULL" for column in column_names])
    print(f'conditions: {conditions}')

    # Удаляем строки, где все значения NULL во всех столбцах, кроме начального telegram_id
    cursor.execute(f"DELETE FROM {table_name} WHERE {conditions}")

    # Фиксируем изменения и закрываем соединение
    connect.commit()
