from datetime import datetime, timedelta

from database.general_db_functions import open_connection, close_connection, v_look_up_many

DATABASE_REG_NAME = 'database/bd.sql'
TABLE_NAME = 'salary'
SALARY_TABLE = ('Report_card_date', 'Author_of_entry', 'Available_to_supervisor',
                # Дата табеля,      Руководитель,       Доступно руководителю,

                'Available_to_employee', 'salary_password', 'Employee_code', 'Position', 'Full_name',
                # Доступно сотруднику,      Пароль заливки,  Код сотрудника,   Должность,    Ф.И.О.,

                'Salary_total', 'Total_motivation', 'Salary_total_plus_Bonus', 'Bonus_vacation_compensation',
                # Итог З/П,     Итог мотивация,     Итог З\П+Бонус,             Премия(компенсация отпуска),

                'Deductions_of_fixed_assets_form_other', 'OS_Deductions_Inventory', 'Deductions_penalties',
                # Вычеты ОС(форма/прочее),                  Вычеты ОС(Инвентаризация),      Вычеты-штрафы

                'Actual_hours_worked', 'Number_of_errors', 'Error_amount', 'Single_output_coefficient',
                # Факт часы,        Кол-во ошибок (примечание), Сумма ошибки,   Единый коэфф.,

                'Additional_work', 'Points_of_given_out', 'Delivery_Points', 'Acceptance_Points',
                # Дополнительные работы Н/Ч, Выдача,    Доставки(Подготовка отгрузок), Приемка,

                'Placement_Points', 'Volume_M3_cross', 'Shipment_Assembly_Points'
                # Размещение,           Объем М3 кросс.,    Сборка отгрузок
                )

TRANSLATE_DICT = {
    'Код.': 'Employee_code',
    'Должность': 'Position',
    'Ф.И.О.': 'Full_name',
    'Итог З/П': 'Salary_total',
    'Итог мотивация': 'Total_motivation',
    'Итог З\П+Бонус': 'Salary_total_plus_Bonus',
    'Премия(компенсация отпуска)': 'Bonus_vacation_compensation',
    'Вычеты ОС(форма/прочее)': 'Deductions_of_fixed_assets_form_other',
    'Вычеты ОС(Инвентаризация)': 'OS_Deductions_Inventory',
    'Вычеты-штрафы': 'Deductions_penalties',
    'Факт часы': 'Actual_hours_worked',
    'Кол-во ошибок (примечание)': 'Number_of_errors',
    'Сумма ошибки': 'Error_amount',
    'Единый коэфф.': 'Single_output_coefficient',
    'Дополнительные работы Н/Ч': 'Additional_work',
    'Выдача ': 'Points_of_given_out',
    'Доставки(Подготовка отгрузок)': 'Delivery_Points',
    'Приемка': 'Acceptance_Points',
    'Размещение': 'Placement_Points',
    'Объем М3 кросс.': 'Volume_M3_cross',
    'Сборка отгрузок': 'Shipment_Assembly_Points'
}


base_column = "Код."
target_column_01 = "Должность"
target_column_02 = "Ф.И.О."
target_column_03 = "Итог З/П"  # Оклад
target_column_04 = "Итог мотивация"  # Премия
target_column_05 = "Итог З\П+Бонус"  # Всего
target_column_06 = "Премия(компенсация отпуска)"
target_column_07 = "Вычеты ОС(форма/прочее)"
target_column_08 = "Вычеты ОС(Инвентаризация)"
target_column_09 = 'Вычеты-штрафы'
target_column_10 = 'Факт часы'
target_column_11 = 'Кол-во ошибок (примечание)'
target_column_12 = 'Сумма ошибки'
target_column_13 = 'Единый коэфф.'
target_column_14 = 'Дополнительные работы Н/Ч'
target_column_15 = 'Выдача '  # <-- пробел после слова - как в файле
target_column_16 = 'Доставки(Подготовка отгрузок)'
target_column_17 = 'Приемка'
target_column_18 = 'Размещение'
target_column_19 = 'Объем М3 кросс.'
target_column_20 = 'Сборка отгрузок'

target_columns = [base_column, target_column_01, target_column_02, target_column_03, target_column_04, target_column_05,
                  target_column_06, target_column_07, target_column_08, target_column_09, target_column_10,
                  target_column_11, target_column_12, target_column_13, target_column_14, target_column_15,
                  target_column_16, target_column_17, target_column_18, target_column_19, target_column_20]


def insert_dict_of_persons_to_database(dict_of_persons: dict, dict_of_filling: dict) -> bool:
    """Функция принимает два словаря: dict_of_persons с данными по сотрудникам и dict_of_filling с данными по заливке
    и проливает их в БД"""

    connect = open_connection(table_name=TABLE_NAME, name_of_columns=SALARY_TABLE)
    cursor = connect.cursor()

    try:
        # Значения из dict_of_filling одинаковы для каждой записи, поэтому их приводим в нужную форму один раз:
        filling_columns_str = ', '.join(dict_of_filling.keys())
        filling_values_str = ', '.join(['?' for _ in dict_of_filling])

        for user_id in dict_of_persons:
            # Для каждого юзера из dict_of_persons формируем запись:
            persons_columns_str = ', '.join(dict_of_persons[user_id].keys()) + ', ' + filling_columns_str
            persons_values_str = ', '.join(['?' for _ in dict_of_persons[user_id]]) + ', ' + filling_values_str

            # Т.к. "столбцы" в dict_of_persons записаны кириллицей, используем переводчик:
            for ru_name in TRANSLATE_DICT:
                persons_columns_str = persons_columns_str.replace(ru_name, TRANSLATE_DICT[ru_name])

            insert_query = f'INSERT INTO {TABLE_NAME} ({persons_columns_str}) VALUES ({persons_values_str})'
            values_tuple = tuple(str(value) for value in dict_of_persons[user_id].values())
            values_tuple += tuple(dict_of_filling.values())
            cursor.execute(insert_query, values_tuple)

            # print(f'Данные юзера {user_id} занесены в БД')
            connect.commit()
        print(f"Все данные из словаря dict_of_persons успешно записаны в БД")
        # display_all_data()
        successful_insert = True
    except Exception as e:
        print(f"Ошибка при вставке данных в БД: {e}")
        successful_insert = False

    # Фиксируем изменения и закрываем соединение
    close_connection(connect=connect)
    return successful_insert


def close_irrelevant_entries(employee_code: str) -> bool:
    """Функция для данного employee_code закрывает все неактуальные записи,
    оставляя только последнюю, если она не старше двух суток"""

    connect = open_connection(table_name=TABLE_NAME, name_of_columns=SALARY_TABLE)
    cursor = connect.cursor()

    # Выбираем все записи сотрудника доступные ему, и упорядочиваем по дате в обратном порядке
    cursor.execute(f'''
        SELECT *
        FROM salary
        WHERE Employee_code = ? AND Available_to_employee = 'True'
        ORDER BY datetime(Report_card_date) DESC
    ''', (employee_code,))
    entries = cursor.fetchall()

    except_entry_from_irrelevant_entries = []  # Список для одной актуальной записи (исключения из неактуальных)
    if len(entries) > 0:
        # Вычисляем даты "сейчас" и "дата записи" для сравнения
        now = datetime.now()
        data_of_entity = datetime.strptime(entries[-1][SALARY_TABLE.index('Report_card_date')], '%d.%m.%y %H:%M')
        # Если последняя по дате запись не вышла за срок годности, помещаем ее в except_entry_from_irrelevant_entries:
        if (now - data_of_entity) <= timedelta(days=5):
            except_entry_from_irrelevant_entries = [entries[-1]]

        # Обновляем записи, устанавливая Available_to_employee в False для всех записей, кроме except_entry_<...>
        for entry in entries:
            if entry not in except_entry_from_irrelevant_entries:
                cursor.execute('''
                    UPDATE salary
                    SET Available_to_employee = 'False'
                    WHERE Employee_code = ? AND Report_card_date = ?
                ''', (employee_code, entry[0]))

    # Фиксируем изменения и закрываем соединение
    close_connection(connect=connect)

    if except_entry_from_irrelevant_entries:
        return True
    else:
        return False


def get_one_record(employee_code: str) -> tuple:
    """Функция извлекает единственную актуальную запись сотрудника и возвращает кортеж"""

    connect = open_connection(table_name=TABLE_NAME, name_of_columns=SALARY_TABLE)
    cursor = connect.cursor()

    # Выбираем единственную доступную запись сотрудника:
    cursor.execute(f'''
        SELECT *
        FROM salary
        WHERE Employee_code = ? AND Available_to_employee = 'True'
    ''', (employee_code,))
    record_of_employee = cursor.fetchone()
    return record_of_employee


def return_the_receipt(employee_code: str) -> str:
    """Функция возвращает текст: квиток, либо сообщение об отсутствии квитка"""

    tuple_of_record = get_one_record(employee_code=employee_code)
    text = make_text_of_receipt(tuple_of_record)

    return text


def make_text_of_receipt(tuple_of_record: tuple) -> str:
    """Формирует текст квитка из кортежа"""

    text = ''
    for i in range(len(target_columns)):
        text += f'{target_columns[i]}: {tuple_of_record[i+5]}\n'
    return text


def get_salary_password_for_user(employee_code: str) -> str:
    salary_password_from_bd = v_look_up_many(
        table_name=TABLE_NAME,
        base_column_names=['Employee_code', 'Available_to_employee'],
        base_column_values=[employee_code, 'True'],
        target_column_name='salary_password'
    )[0]
    return salary_password_from_bd

