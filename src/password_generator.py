import secrets
import string


def generate_password(length: int = None) -> str:
    """Генерирует случайный сложный пароль."""

    # Возможные символы
    characters = string.ascii_letters + string.digits + string.punctuation

    # Случайная длина от 12 до 24 символов
    if length is None:
        length = 12 + secrets.randbelow(12)

    while True:
        # Генерация пароля
        password = "".join(secrets.choice(characters) for _ in range(length))

        # Проверка на наличие букв, цифр и знаков
        if (any(c.islower() for c in password)
                and any(c.isupper() for c in password)
                and any(c.isdigit() for c in password)
                and any(c in string.punctuation for c in password)):
            return password
