from typing import Tuple

from database.general_db_functions import get_data_from_column, update_data_in_column, open_connection, \
    display_all_data_from_table, close_connection

TABLE_NAME = 'users'
REGISTRATION_TABLE = ('telegram_id', 'telegram_username', 'state_in_bot',
                      'employee_code', 'secret_employee_code', 'registration_attempts')


def get_user_state_from_db(telegram_id: str) -> str | bool:
    """Функция возвращает значение state_in_bot в таблице TABLE_NAME для пользователя telegram_id"""

    value = get_data_from_column(
        table_name=TABLE_NAME,
        base_column_name='telegram_id',
        base_column_value=telegram_id,
        target_column_name='state_in_bot'
    )[0]
    if value != "":
        return value
    else:
        return False


def save_user_state_to_db(telegram_id: str, new_state: str) -> None:
    """Функция обновляет значение state_in_bot в таблице TABLE_NAME для пользователя telegram_id"""

    update_data_in_column(
        table_name=TABLE_NAME,
        base_column_name='telegram_id',
        base_column_value=telegram_id,
        target_column_name='state_in_bot',
        new_value=new_state
    )


def insert_user_to_database(reg_table: Tuple[str, ...]) -> bool:
    """Функция записывает в таблицу TABLE_NAME нового юзера, если юзер не существует"""

    connect = open_connection(table_name=TABLE_NAME, name_of_columns=REGISTRATION_TABLE)
    cursor = connect.cursor()

    # Распаковываем кортеж reg_table (вообще, нам нужен только telegram_id, но для наглядности раскидываем всё):
    telegram_id, telegram_username, state_in_bot, employee_code, secret_employee_code, registration_attempts = reg_table

    # Проверяем наличие данных для указанного telegram_id
    select_query = f'SELECT * FROM {TABLE_NAME} WHERE telegram_id = ?'
    cursor.execute(select_query, (telegram_id,))
    existing_data = cursor.fetchone()

    if existing_data:
        # Если данный юзер уже существует, ничего вставлять не надо:
        print(f"Юзер {telegram_id}: данные уже есть БД")
        successful_insert = False
    else:
        # Если данного юзера нет, вставляем новую запись
        insert_query = f'INSERT INTO {TABLE_NAME} (telegram_id, telegram_username, state_in_bot, employee_code, ' \
                       'secret_employee_code, registration_attempts) VALUES (?, ?, ?, ?, ?, ?)'
        cursor.execute(insert_query, reg_table)
        print(f"Юзер {telegram_id}: данные успешно записаны в БД")

        display_all_data_from_table(table_name=TABLE_NAME)
        successful_insert = True

    # Фиксируем изменения и закрываем соединение
    close_connection(connect=connect)
    return successful_insert
