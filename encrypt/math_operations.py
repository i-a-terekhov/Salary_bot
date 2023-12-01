from encrypt.crypto_engine import CRYPT_KEY_NUM, encrypt_text_number, decrypt_text


def check_employee_code(user_input: str) -> str | bool:
    """ Возвращает 'секретный код сотрудника', если удается конвертировать полученный ввод от клиента, иначе - False"""
    it_is_digit = False
    if 4 <= len(user_input) <= 6:
        try:
            _ = int(user_input)
            it_is_digit = True
        except Exception as e:
            print('Не удалось конвертировать запись пользователя в число', e)

        if it_is_digit:
            return encrypt_text_number(user_input, crypt_key=CRYPT_KEY_NUM)

    else:
        print('Код сотрудника состоит из 4-6 цифр')
        return False

def check_secret_employee_code(user_input: str, user_employee_code: str) -> str | bool:
    pass