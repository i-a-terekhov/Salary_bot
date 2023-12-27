from encrypt.crypto_engine import CRYPT_KEY_NUM, encrypt_text_number


def check_employee_code(user_input: str) -> str | bool:
    """ Возвращает 'секретный код сотрудника', если удается конвертировать полученный ввод от клиента, иначе - False"""
    # print('Функция проверки Кода сотрудника: ', end='')
    it_is_digit = False
    if 4 <= len(user_input) <= 6:
        try:
            _ = int(user_input)
            it_is_digit = True
        except Exception as e:
            # print('Не удалось конвертировать запись пользователя в число', e)
            pass

        if it_is_digit:
            # print('ОК')
            return encrypt_text_number(user_input, crypt_key=CRYPT_KEY_NUM)

    else:
        # print('Код сотрудника состоит из 4-6 цифр')
        return False
