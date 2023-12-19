from typing import Tuple

from database.general_db_functions import get_data_from_column, update_data_in_column, open_connection, \
    display_all_data_from_table, close_connection

TABLE_NAME = 'users'
REGISTRATION_TABLE = ('telegram_id', 'telegram_username', 'state_in_bot',
                      'employee_code', 'secret_employee_code', 'registration_attempts')


def get_user_state_from_db(telegram_id: str) -> str | bool:
    target_column = 'state_in_bot'
    value = get_data_from_column(telegram_id=telegram_id, column=target_column)
    if value != "":
        return value
    else:
        return False


def save_user_state_to_db(telegram_id: str, new_state: str) -> None:
    target_column = 'state_in_bot'
    update_data_in_column(base_column_name=telegram_id, target_column_name=target_column, new_value=new_state)


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
        display_all_data_from_table()
        successful_insert = True

    # Фиксируем изменения и закрываем соединение
    close_connection(connect=connect)
    return successful_insert
