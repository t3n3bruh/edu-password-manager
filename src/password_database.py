import sqlite3


class PasswordDatabase:
    """Класс БД, хранит данные аккаунтов."""

    def __init__(self, db_path: str = "database.db"):
        """Создает БД по заданному пути."""

        # Соединение с БД.
        self.connection = sqlite3.connect(db_path)
        self.cursor = self.connection.cursor()

        # Начальное создание таблицы.
        self.cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS Data (
                entry_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                service_name TEXT NOT NULL,
                login TEXT NOT NULL,
                encrypted_password BLOB NOT NULL
            )
            '''
        )
        self.connection.commit()

    def __del__(self):
        """Закрывает соединение с БД."""

        self.cursor.close()
        self.connection.close()

    def is_empty(self) -> bool:
        """Проверяет, пуста ли БД."""

        # Выполнение запроса.
        self.cursor.execute("SELECT EXISTS (SELECT 1 FROM Data);")

        # Проверка на пустоту.
        if self.cursor.fetchone()[0] == 0:
            return True
        else:
            return False

    def get_all(self) -> list:
        """Возвращает все записи."""

        # Выполнение запроса.
        self.cursor.execute("SELECT * FROM Data")
        self.connection.commit()

        # Возврат результата.
        return self.cursor.fetchall()

    def get_entries(self, count: int, offset: int = 0) -> list:
        """Возвращает <count> записей со смещением <offset>."""

        # Выполнение запроса.
        self.cursor.execute(
            '''
            SELECT * FROM Data
            LIMIT ? OFFSET ?
            ''',
            (count, offset)
        )
        self.connection.commit()

        # Возврат результата.
        return self.cursor.fetchall()

    def find_entries(self, substring: str, count: int, offset: int) -> list:
        """Возвращает записи с вхождением подстроки в имени сервиса."""

        # Выполнение запроса.
        self.cursor.execute(
            '''
            SELECT * FROM Data
            WHERE service_name LIKE ?
            LIMIT ? OFFSET ?
            ''',
            ('%{}%'.format(substring), count, offset)
        )
        self.connection.commit()

        # Возврат результата.
        return self.cursor.fetchall()

    def add_entry(self, service_name: str, login: str, encrypted_password: bytes) -> None:
        """Добавляет новую запись с переданными данными."""

        # Выполнение запроса.
        self.cursor.execute(
            '''
            INSERT INTO Data (service_name, login, encrypted_password)
            VALUES (?, ?, ?)
            ''',
            (service_name, login, encrypted_password)
        )
        self.connection.commit()

    def update_entry(self, entry_id: int, service_name: str, login: str, encrypted_password: bytes = None) -> None:
        """Обновляет запись с индексом <entry_id>."""

        # Если пароль не передан, то не меняет пароль в записи.
        if encrypted_password is None:
            self.cursor.execute(
                '''
                UPDATE Data
                SET service_name = ?, login = ?
                WHERE entry_id = ?
                ''',
                (service_name, login, entry_id)
            )
        # Если пароль передан, то обновляет пароль в записи.
        else:
            self.cursor.execute(
                '''
                UPDATE Data
                SET service_name = ?, login = ?, encrypted_password = ?
                WHERE entry_id = ?
                ''',
                (service_name, login, encrypted_password, entry_id)
            )
        self.connection.commit()

    def delete_entry(self, entry_id: int) -> None:
        """Удаляет запись с индексом <entry_id>."""

        # Выполнение запроса.
        self.cursor.execute(
            '''
            DELETE FROM Data
            WHERE entry_id = ?
            ''',
            (entry_id,)
        )
        self.connection.commit()
