from typing import Tuple

from database.general_db_functions import open_connection, close_connection, display_all_data

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


