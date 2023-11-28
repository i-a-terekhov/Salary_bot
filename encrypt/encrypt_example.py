from encrypt.crypto_engine import encrypt_text_number, decrypt_text

# Пример использования
list_number_to_encrypt = [1111, 54321, 78777, 98774, 21424, 45554, 91111, 45555, 45556, 45557, 33333, 34566, 23433]
CRYPT_KEY_NUM = 4

for number_to_encrypt in list_number_to_encrypt:
    encrypted_text = encrypt_text_number(str(number_to_encrypt), crypt_key=CRYPT_KEY_NUM)
    decrypted_number = decrypt_text(encrypted_text, crypt_key=CRYPT_KEY_NUM)

    print(f"Original Number: {number_to_encrypt}")
    print(f"Encrypted Text: {encrypted_text}")
    # print(f"Decrypted Number: {decrypted_number}")
    print('-' * 30)
