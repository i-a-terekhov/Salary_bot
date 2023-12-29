from datetime import datetime, timedelta

from database.general_db_functions import open_connection, close_connection

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


def get_one_record(employee_code: str) -> None:
    connect = open_connection(table_name=TABLE_NAME, name_of_columns=SALARY_TABLE)
    cursor = connect.cursor()

    # Выбираем единственную доступную запись сотрудника:
    cursor.execute(f'''
        SELECT *
        FROM salary
        WHERE Employee_code = ? AND Available_to_employee = 'True'
    ''', (employee_code,))
    record_of_employee = cursor.fetchone()
    print(record_of_employee)


def return_the_receipt(employee_code: str) -> None:
    """Функция возвращает квиток"""
    print('return_the_receipt')

    if close_irrelevant_entries(employee_code=employee_code):
        print('Найдена актуальная запись:')
        get_one_record(employee_code=employee_code)
    else:
        # Актуального расчетного листа не найдено
        pass
