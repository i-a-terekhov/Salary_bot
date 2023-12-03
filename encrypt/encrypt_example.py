from encrypt.crypto_engine import encrypt_text_number, decrypt_text
from encrypt.crypto_engine import primal_dict

# # Пример использования
list_number_to_encrypt = [1111, 54321, 78777, 98774, 21424, 45554, 91111, 45555, 45556, 45557, 33333, 34566, 23433,
                          55555]
# list_number_to_encrypt = ['95005', '95006', '95069', '95079', '95106', '95116', '95170', '95179', '95267', '95277', '95278', '95285', '95286', '95296', '95378', '95396', '95807', '95889', '95907', '95908', '95918', '95989', '95990', '95999', '96116', '96170', '96378', '96396', '96918', '96990', '99001', '99029', '99227', '99281', '99407', '99489']
#
CRYPT_KEY_NUM = 4
#
for number_to_encrypt in list_number_to_encrypt:
    encrypted_text = encrypt_text_number(str(number_to_encrypt), crypt_key=CRYPT_KEY_NUM)
    decrypted_number = decrypt_text(encrypted_text, crypt_key=CRYPT_KEY_NUM)
#
    print(f"Original Number: {number_to_encrypt}")
    print(f"Encrypted Text: {encrypted_text}")
    # print(f"Decrypted Number: {decrypted_number}")
    print('-' * 30)


# print(f"Пример расшифровки: {decrypt_text('0000-0000-0000-00')}")
# print(f"Пример расшифровки: {decrypt_text('1111-1111-1111-11')}")
# print(f"Пример расшифровки: {decrypt_text('2222-2222-2222-22')}")

# ----------------------------------------------------------------------------------------------------------------------
# # test encrypt_text_number
# encrypt_dict = {}
# k = 0
# j = 0
# for i in range(1000, 999999):
#     j += 1
#     encrypt_i = encrypt_text_number(str(i), crypt_key=CRYPT_KEY_NUM)
#
#     if encrypt_i not in encrypt_dict:
#         encrypt_dict[encrypt_i] = [i]
#     else:
#         k += 1
#         encrypt_dict[encrypt_i].append(i)
#         if len(encrypt_dict[encrypt_i]) >= 4:
#             print(encrypt_dict[encrypt_i])
#
# # filtered_dict = {key: value for key, value in encrypt_dict.items() if len(value) > 1}
# print(k, '-', j)

# ----------------------------------------------------------------------------------------------------------------------
print(f'Всего комбинаций 10^8 = {10**8}, т.к. есть 8 разрядов (16 знаков, где каждые два знака - это 1 исход. цифра)')
print(f'Из 8-ми цифр только 5 значащих (код сотрудника), остальные 3 цифры добавляются в процессе шифрования')
print(f'Т.е. каждый код сотрудника может быть зашифрован 10^3 = {10**3} способом, т.к. 3 разряда могут быть любыми')
print(f'Делим 10^8 = {10**8} на 10^3 = {10**3}, получая {(10**8) / (10**3)}, или {10**5}')
print(f'Всего кодов сотрудника 10^5 = {10**5})')
print(f'Т.е. таких комбинаций "Зашифрованных кодов сотрудников", '
      f'которые не приведут к проверке в боте = {10**8 - 10**5},'
      f'\nпотому что бот сравнивает "Секретный код сотрудника", полученный от функции шифрования "Кода сотрудника"\n'
      f'с тем "Секретным кодом сотрудника", который пользователь будет вводить вручную')

# ----------------------------------------------------------------------------------------------------------------------
# Набор символов (каждый символ состоит из двух букв) # too heavy operation!
symbols = [
    primal_dict['0'][CRYPT_KEY_NUM],
    primal_dict['1'][CRYPT_KEY_NUM],
    primal_dict['2'][CRYPT_KEY_NUM],
    # primal_dict['3'][CRYPT_KEY_NUM],
    # primal_dict['4'][CRYPT_KEY_NUM],
    # primal_dict['5'][CRYPT_KEY_NUM],
    # primal_dict['6'][CRYPT_KEY_NUM],
    # primal_dict['7'][CRYPT_KEY_NUM],
    # primal_dict['8'][CRYPT_KEY_NUM],
    # primal_dict['9'][CRYPT_KEY_NUM],
]

# Длина комбинации
combination_length = 16

# Генерация всех комбинаций
combinations = []


def generate_combinations(prefix, remaining_length):
    if remaining_length == 0:
        combinations.append(prefix)
        return
    for symbol in symbols:
        generate_combinations(prefix + symbol, remaining_length - 2)


# Начинаем генерацию с пустого префикса и полной длины
generate_combinations("", combination_length)

# # Вывод результатов
print('-' * 100)
# print(combinations)
print(f'Имея только {len(symbols)} символа для комбинации '
      f'можно сгенерировать {len(symbols)}^8 = {len(combinations)} "Секретных кодов"')

# ----------------------------------------------------------------------------------------------------------------------
# test decrypt_text_number  # too heavy operation!
decrypt_dict = {}
k = 0
j = 0
set_of_numbers = set()
for i in combinations:
    a, b, c, d = i[:4], i[4:8], i[8:12], i[12:]
    blocked_text = a + '-' + b + '-' + c + '-' + d
    j += 1
    # print(blocked_text)
    decrypt_i = decrypt_text(blocked_text, crypt_key=CRYPT_KEY_NUM)
    set_of_numbers.add(decrypt_i)

    a, b, c = blocked_text[:2], blocked_text[4:10], blocked_text[12:]
    blocked_text_without = a + 'ХХ' + b + 'ХХ' + c

    if decrypt_i not in decrypt_dict:
        decrypt_dict[decrypt_i] = set()
        decrypt_dict[decrypt_i].add(blocked_text_without)
    else:
        k += 1
        decrypt_dict[decrypt_i].add(blocked_text_without)
        if len(decrypt_dict[decrypt_i]) >= 16:
            print(decrypt_i, ': ', decrypt_dict[decrypt_i])

print('-' * 100)
print(f'Из рассмотренных {j} "Секретных кодов сотрудников", не пройдут проверку в боте {k}, или {k/j}%')
print('-' * 100)

# print(set_of_numbers)
# print(decrypt_dict)


