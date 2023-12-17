import sqlite3
from sqlite3 import Connection, Error
from typing import List, Tuple

DATABASE_REG_NAME = 'database/bd.sql'
TABLE_NAME = 'salary'
SALARY_TABLE = ('Report_card_date', 'author_of_entry', 'available_to_supervisor', 'password_attempts',
                # Дата табеля,      Руководитель,       Доступно руководителю,      Попыток ввода пароля,

                'available_to_employee', 'secret_employee_code', 'employee_code', 'Position', 'Full_name',
                # Доступно сотруднику,  Секретный код сотрудника, Код сотрудника,   Должность,    Ф.И.О.,

                'Salary_total', 'Total_motivation', 'Salary_total_plus_Bonus', 'Bonus_(vacation_compensation)',
                # Итог З/П,     Итог мотивация,     Итог З\П+Бонус,             Премия(компенсация отпуска),

                'Deductions_of_fixed_assets_(form/other)', 'OS_Deductions_(Inventory)', 'Deductions-penalties',
                # Вычеты ОС(форма/прочее),                  Вычеты ОС(Инвентаризация),      Вычеты-штрафы

                'Actual_hours_worked', 'Number_of_errors', 'Error_amount', 'Single_output_coefficient',
                # Факт часы,        Кол-во ошибок (примечание), Сумма ошибки,   Единый коэфф.,

                'Additional_work', 'Points_of_given_out', 'Delivery_Points', 'Acceptance_Points',
                # Дополнительные работы Н/Ч, Выдача,    Доставки(Подготовка отгрузок), Приемка,

                'Placement_Points', 'Volume_M3_cross', 'Shipment_Assembly_Points'
                # Размещение,           Объем М3 кросс.,    Сборка отгрузок
                )


def open_connection(db_name: str = DATABASE_REG_NAME, name_of_columns: Tuple[str] = SALARY_TABLE) -> Connection:
    # Открываем или создаем базу данных
    connect = sqlite3.connect(db_name)
    cursor = connect.cursor()

    # Формируем строку с именами столбцов
    columns_str = ', '.join([f"{column} TEXT" for column in name_of_columns])

    # Создаем таблицу с динамически формированными столбцами
    create_table_query = '''
        CREATE TABLE IF NOT EXISTS {} (
            {}
        )
    '''.format(TABLE_NAME, columns_str)

    cursor.execute(create_table_query)
    return connect


def close_connection(connect: Connection) -> None:
    connect.commit()
    connect.close()


def test_connection(required_columns: Tuple[str] = SALARY_TABLE) -> bool:
    print('Проверка подключения к БД: ', end='')
    try:
        connect = open_connection()
        cursor = connect.cursor()

        # Проверяем существование таблицы и ее структуру
        cursor.execute(f'''
            PRAGMA table_info({TABLE_NAME})
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


def insert_user_to_database(user_data: dict) -> bool:
    connect = open_connection()
    cursor = connect.cursor()

    try:
        # Вставляем новую запись
        insert_query = f'INSERT INTO {TABLE_NAME} (' + ', '.join(user_data.keys()) + ') VALUES (' + ', '.join(['?'] * len(user_data)) + ')'
        cursor.execute(insert_query, tuple(user_data.values()))
        connect.commit()
        print(f"Пользователь {user_data['telegram_id']}: данные успешно записаны в БД")
        display_all_data()
        successful_insert = True
    except Exception as e:
        print(f"Ошибка при вставке пользователя в БД: {e}")
        successful_insert = False

    # Фиксируем изменения и закрываем соединение
    close_connection(connect=connect)
    return successful_insert


#TODO функция не работает
def update_data_in_column(telegram_id: str, column: str, value: str) -> None:
    connect = open_connection()
    cursor = connect.cursor()

    update_query = f'UPDATE {TABLE_NAME} SET {column} = ? WHERE telegram_id = ?'
    cursor.execute(update_query, (value, telegram_id))
    print(f"Для юзера {telegram_id} обновлено значение в столбце {column} на {value}")

    close_connection(connect=connect)


def display_all_data() -> None:
    connect = open_connection()
    cursor = connect.cursor()

    # Выбираем все строки из таблицы salary
    select_all_query = f'SELECT * FROM {TABLE_NAME}'
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
