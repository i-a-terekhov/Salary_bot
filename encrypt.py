from hidden.crypto import encrypt_number, decrypt_text

# Пример использования
list_number_to_encrypt = [1111, 54321, 78777, 98774, 21424, 76687, 324435, 234523]
no = 3

for number_to_encrypt in list_number_to_encrypt:
    encrypted_text = encrypt_number(number_to_encrypt, no=no)
    decrypted_number = decrypt_text(encrypted_text, no=no)
    print(f"Original Number: {number_to_encrypt}")
    print(f"Encrypted Text: {encrypted_text}")
    print(f"Decrypted Number: {decrypted_number}")
    print('-' * 30)
