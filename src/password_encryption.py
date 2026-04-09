import hashlib
import base64
from cryptography.fernet import Fernet


class PasswordEncryption:
    """Реализует шифрование и расшифрование паролей."""

    def __init__(self, password: str) -> None:
        """Создает шифровщик на основе пароля."""

        self.fernet = Fernet(self.generate_key(password))

    @classmethod
    def generate_key(cls, password: str) -> bytes:
        """Генерирует ключ на основе пароля."""

        # Генерация хеша пароля и получение ключа длиной 32 байта
        key = hashlib.sha256(password.encode()).digest()

        # Возврат URL-safe base64 ключа
        return base64.urlsafe_b64encode(key)

    def encrypt(self, data: str) -> bytes:
        """Шифрует строку."""

        encrypted_data = self.fernet.encrypt(data.encode())
        return encrypted_data

    def decrypt(self, data: bytes) -> str:
        """Расшифровывает данные."""

        decrypted_message = self.fernet.decrypt(data)
        return decrypted_message.decode()
