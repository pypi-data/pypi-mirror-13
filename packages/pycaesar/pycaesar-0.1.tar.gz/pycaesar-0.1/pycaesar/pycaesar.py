A_DECIMAL_ASCII_REPRESENTATION = 65
Z_DECIMAL_ASCII_REPRESENTATION = 90
a_DECIMAL_ASCII_REPRESENTATION = 97
z_DECIMAL_ASCII_REPRESENTATION = 122


def encrypt(message, key):
    try:
        key = int(key)
        if key > 0 and key < 26:
            return ''.join([_encrypt_letter(letter, key) for letter in message])
        else:
            raise ValueError
    except ValueError:
        raise ValueError('Please use a valid integer key between 1 and 25.')


def _encrypt_letter(plain_letter, key):
    encrypted_letter_number = ord(plain_letter) + key
    if plain_letter.isalpha():
        if plain_letter == plain_letter.lower():
            encrypted_letter_number = _encrypt_lower_case(encrypted_letter_number)
        else:
            encrypted_letter_number = _encrypt_upper_case(encrypted_letter_number)
        return chr(encrypted_letter_number)
    else:
        return plain_letter


def _encrypt_lower_case(encrypted_letter_number):
    number_of_letters_after_last_letter = encrypted_letter_number - (z_DECIMAL_ASCII_REPRESENTATION + 1)
    # TODO: this is too messy, find a way to get rid of +1
    if number_of_letters_after_last_letter < 0:
        return encrypted_letter_number
    else:
        return a_DECIMAL_ASCII_REPRESENTATION + number_of_letters_after_last_letter


def _encrypt_upper_case(encrypted_letter_number):
    number_of_letters_after_last_letter = encrypted_letter_number - (Z_DECIMAL_ASCII_REPRESENTATION + 1)
    # TODO: this is too messy, find a way to get rid of +1
    if number_of_letters_after_last_letter < 0:
        return encrypted_letter_number
    else:
        return A_DECIMAL_ASCII_REPRESENTATION + number_of_letters_after_last_letter


def decrypt(cipher_text, key):
    try:
        key = int(key)
        if 0 < key < 26:
            return ''.join([_decrypt_letter(cipher_letter, key) for cipher_letter in cipher_text])
        else:
            raise ValueError
    except ValueError:
        raise ValueError('Please use a valid integer key between 1 and 25.')


def _decrypt_letter(cipher_letter, key):
    plain_letter_number = ord(cipher_letter) - key
    if cipher_letter.isalpha():
        if cipher_letter == cipher_letter.lower():
            plain_letter_number = _decrypt_lower_case(plain_letter_number)
        else:
            plain_letter_number = _decrypt_upper_case(plain_letter_number)
        return chr(plain_letter_number)
    else:
        return cipher_letter


def _decrypt_lower_case(plain_letter_number):
    number_of_letters_before_first_letter = plain_letter_number - a_DECIMAL_ASCII_REPRESENTATION + 1
    # TODO: this is too messy, find a way to get rid of +1
    if plain_letter_number < a_DECIMAL_ASCII_REPRESENTATION:
        return z_DECIMAL_ASCII_REPRESENTATION + number_of_letters_before_first_letter
    else:
        return plain_letter_number


def _decrypt_upper_case(plain_letter_number):
    number_of_letters_before_first_letter = plain_letter_number - A_DECIMAL_ASCII_REPRESENTATION + 1
    # TODO: this is too messy, find a way to get rid of +1
    if plain_letter_number < A_DECIMAL_ASCII_REPRESENTATION:
        return Z_DECIMAL_ASCII_REPRESENTATION + number_of_letters_before_first_letter
    else:
        return plain_letter_number
