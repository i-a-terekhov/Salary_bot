from encrypt.crypto_engine import encrypt_text_number, decrypt_text
from encrypt.crypto_engine import primal_dict

# Пример использования
list_number_to_encrypt = [1111, 54321, 78777, 98774, 21424, 45554, 91111, 45555, 45556, 45557, 33333, 34566, 23433, 55555]
CRYPT_KEY_NUM = 4

# for number_to_encrypt in list_number_to_encrypt:
#     encrypted_text = encrypt_text_number(str(number_to_encrypt), crypt_key=CRYPT_KEY_NUM)
#     decrypted_number = decrypt_text(encrypted_text, crypt_key=CRYPT_KEY_NUM)
#
#     print(f"Original Number: {number_to_encrypt}")
#     print(f"Encrypted Text: {encrypted_text}")
#     # print(f"Decrypted Number: {decrypted_number}")
#     print('-' * 30)


# print(f"Пример расшифровки: {decrypt_text('0000-0000-0000-00')}")
# print(f"Пример расшифровки: {decrypt_text('1111-1111-1111-11')}")
# print(f"Пример расшифровки: {decrypt_text('2222-2222-2222-22')}")


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



# Набор символов (каждый символ состоит из двух букв)
symbols = [
    primal_dict['0'][CRYPT_KEY_NUM],
    primal_dict['1'][CRYPT_KEY_NUM],
    primal_dict['2'][CRYPT_KEY_NUM],
    primal_dict['3'][CRYPT_KEY_NUM],
    primal_dict['4'][CRYPT_KEY_NUM],
    primal_dict['5'][CRYPT_KEY_NUM],
    primal_dict['6'][CRYPT_KEY_NUM],
    primal_dict['7'][CRYPT_KEY_NUM],
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
# for combo in combinations:
#     print(combo)


# test decrypt_text_number
decrypt_dict = {}
k = 0
j = 0
for i in combinations:
    j += 1
    decrypt_i = encrypt_text_number(str(i), crypt_key=CRYPT_KEY_NUM)

    if decrypt_i not in decrypt_dict:
        decrypt_dict[decrypt_i] = [i]
    else:
        k += 1
        decrypt_dict[decrypt_i].append(i)
        if len(decrypt_dict[decrypt_i]) >= 4:
            print(decrypt_dict[decrypt_i])

# # filtered_dict = {key: value for key, value in encrypt_dict.items() if len(value) > 1}
print(k, '-', j)  # 0 - 16777216

