import tkinter as tk
from tkinter import ttk
from cryptography.fernet import InvalidToken
from src.password_generator import generate_password
from src.password_encryption import PasswordEncryption
from src.password_database import PasswordDatabase


class PasswordManager:
    """
    Главный класс приложения.
    Хранит экземпляры классов и настройки стилей.
    """

    def __init__(self):

        # Главное окно
        self.root = tk.Tk()
        self.root.title("Менеджер паролей")
        self.root.geometry("320x480")
        self.root.resizable(False, False)

        # База данных
        self.db = PasswordDatabase("database.db")

        # Модуль шифрования
        self.encryption: PasswordEncryption

        # Параметры внешнего вида
        self.style = ttk.Style()
        self.color_primary = "sea green"
        self.color_secondary = "gray16"
        self.color_tetriary = "gray24"

        # Виджеты
        self.page_entry_list = PageEntryList(self)
        self.page_request_password = PageRequestPassword(self)
        self.page_add_or_update = PageAddOrUpdate(self)

        # Начало работы
        self.config_style()
        self.page_request_password.show()

    def config_style(self) -> None:
        """Задает внешний вид приложения, перенастраивая стили по-умолчанию."""

        self.style.theme_use("clam")
        ttk.Style().configure(
            "TLabelframe",
            padding=8,
            background=self.color_secondary,
            bordercolor=self.color_primary,
            relief="solid",
            labeloutside=False,
            labelmargins=[10, 0, 0, 0]
        )

        ttk.Style().configure(
            "TFrame",
            padding=8,
            background=self.color_secondary,
            bordercolor=self.color_primary,
            relief="solid"
        )

        ttk.Style().configure(
            "TLabelframe.Label",
            background=self.color_secondary,
            foreground=self.color_primary,
            font=('Helvetica', 14)
        )

        ttk.Style().configure(
            "TEntry",
            background=self.color_secondary,
            foreground=self.color_primary,
            fieldbackground=self.color_tetriary,
            bordercolor=self.color_primary,
            selectborderwidth=0,
            relief="solid",
            lightcolor=self.color_secondary
        )

        ttk.Style().configure(
            "TButton",
            font=('Helvetica', 14),
            background=self.color_secondary,
            foreground=self.color_primary,
            bordercolor=self.color_primary,
            relief="solid"
        )

        ttk.Style().configure(
            "TLabel",
            background=self.color_secondary,
            foreground=self.color_primary,
            font=('Helvetica', 14)
        )

        self.root.configure(background=self.color_secondary)

    def run(self) -> None:
        """Запуск приложения."""

        self.root.mainloop()


class PageEntryList:
    """
    Главная страница.
    Реализует список с данными учетных записей и поиск по имени сервиса.
    """

    def __init__(self, pm: PasswordManager):

        # Главный класс приложения.
        self.pm = pm

        # Номер страницы.
        self.page_num = tk.StringVar(value="1")

        # Переменная для поля поиска.
        self.search_var = tk.StringVar(value="")

        # Вызов функции при изменении значения поля поиска.
        self.search_var.trace_add("write", self.search_callback)

        # Лимит отображения записей в списке.
        self.list_entry_limit = 4

        # Контейнер для поля поиска.
        self.search_frame = ttk.Labelframe(
            self.pm.root,
            labelanchor="nw",
            text=" Поиск: ",
        )

        # Поле поиска.
        self.search_entry = ttk.Entry(
            self.search_frame,
            font=('Helvetica', 14),
            justify="left",
            textvariable=self.search_var,
            cursor="draft_large"
        )

        # Контейнер для списка записей.
        self.list_frame = ttk.Frame(
            self.pm.root
        )

        # Кнопка добавления записи при пустом списке.
        self.add_button = ttk.Button(
            self.list_frame,
            text="Добавить",
            command=self.add_entry
        )

        # Сообщение при отсутствии результатов поиска.
        self.search_label = ttk.Label(
            self.list_frame,
            justify="left",
            text="Не удалось найти записи, \nподходящие под условия \nпоиска."
        )

        # Контейнер элементов навигации.
        self.navigation_frame = ttk.Frame(
            self.pm.root
        )

        # Кнопка перехода на предыдущие записи.
        self.prev_button = ttk.Button(
            self.navigation_frame,
            text="<",
            width=2,
            command=lambda i=-1: self.button_click(i)
        )

        # Номер страницы.
        self.page_num_label = ttk.Label(
            self.navigation_frame,
            textvariable=self.page_num,
            justify="center",
            width=2
        )

        # Кнопка перехода на следующие записи.
        self.next_button = ttk.Button(
            self.navigation_frame,
            text=">",
            width=2,
            command=lambda j=1: self.button_click(j)
        )

        # Загрузка первых 5 записей при первой загрузке приложения.
        self.list_show_page(1)

    def show(self) -> None:
        """Отображает виджеты страницы."""

        self.search_frame.pack(
            expand=False,
            fill="x",
            padx=12,
            pady=(12, 0)
        )
        self.search_entry.pack(
            side="left",
            fill="x",
            expand=True
        )
        self.list_frame.pack(
            fill="both",
            expand=True,
            padx=12,
            pady=(12, 0)
        )
        self.navigation_frame.pack(
            expand=False,
            fill="x",
            padx=12,
            pady=(12, 12)
        )
        self.prev_button.pack(
            side="left",
            padx=12,
            pady=12
        )
        self.page_num_label.pack(
            expand=True,
            side="left",
            padx=12,
            pady=12
        )
        self.next_button.pack(
            side="right",
            padx=12,
            pady=12
        )

    def hide(self) -> None:
        """Скрывает виджеты страницы."""

        self.search_frame.pack_forget()
        self.list_frame.pack_forget()
        self.navigation_frame.pack_forget()

    def list_clear(self) -> None:
        """Очищает список от всех записей."""

        for entry in self.list_frame.winfo_children():
            if type(entry) is ttk.Frame:
                entry.destroy()

    def list_show_page(self, page: int) -> None:
        """Осуществляет переход на указанную страницу."""

        self.list_clear()
        self.add_button.pack_forget()
        self.search_label.pack_forget()

        # Загрузка данных из БД.
        entries: list
        if not self.search_var.get():
            # Без фильтрации по сервису:
            entries = self.pm.db.get_entries(self.list_entry_limit, (page - 1) * self.list_entry_limit)
        else:
            # С фильтрацией по сервису:
            entries = self.pm.db.find_entries(
                self.search_var.get(),
                self.list_entry_limit,
                (page - 1) * self.list_entry_limit)

        # Создание новых записей в списке.
        if entries:
            for entry in entries:
                i = ListEntry(
                    self.pm,
                    self.list_frame,
                    entry[0],
                    entry[1],
                    entry[2],
                    entry[3],
                )
                i.entry_frame.pack(
                    expand=False,
                    fill="x",
                    anchor="n",
                    padx=12,
                    pady=(12, 0)
                )
        # Если нет записей для загрузки в список:
        else:
            if not self.search_var.get():
                # Отображение кнопки добавления записи.
                self.add_button.pack(
                    anchor="n",
                    pady=12
                )
            else:
                # Отображение сообщения об отсутствии результатов поиска.
                self.search_label.pack(
                    anchor="n",
                    padx=12,
                    pady=12
                )

        # Обновление номера страницы.
        self.page_num.set(str(page))

    def add_entry(self) -> None:
        """Метод для кнопки создания записи."""

        self.pm.page_add_or_update.mode_add()
        self.hide()
        self.pm.page_add_or_update.show()

    def button_click(self, step: int) -> None:
        """Метод для кнопок навигации по страницам списка."""

        # Страница для перехода.
        page = int(self.page_num.get()) + step

        # Валидация значения.
        if page <= 0:
            return
        elif not self.search_var.get():
            if len(self.pm.db.get_entries(
                    self.list_entry_limit,
                    (page - 1) * self.list_entry_limit
            )) == 0:
                return
        else:
            if len(self.pm.db.find_entries(
                    self.search_var.get(),
                    self.list_entry_limit,
                    (page - 1) * self.list_entry_limit
            )) == 0:
                return

        # Переход на страницу списка.
        self.list_show_page(page)

    def search_callback(self, *args) -> None:
        """Метод для поля поиска. Обновляет список после изменения поиска."""

        self.list_show_page(1)


class ListEntry:
    """
    Класс одной записи в списке на главной странице.
    Содержит данные одной учетной записи, реализует работу с данными через контекстное меню.
    """

    def __init__(
            self,
            pm: PasswordManager,
            container: tk.Widget,
            entry_id: int,
            service_name: str,
            login: str,
            encrypted_password: bytes
    ):

        # Главный класс приложения.
        self.pm = pm

        # Данные одной записи БД.
        self.entry_id = entry_id
        self.service_name = service_name
        self.login = login
        self.encrypted_password = encrypted_password

        # Контейнер записи.
        self.entry_frame = ttk.Frame(
            container,
            cursor="draft_large",
        )

        # Контекстное меню.
        self.context_menu = tk.Menu(self.entry_frame, tearoff=0)
        self.context_menu.add_command(label="Копировать пароль", command=self.copy_password)
        self.context_menu.add_command(label="Добавить", command=self.add_entry)
        self.context_menu.add_command(label="Изменить", command=self.update_entry)
        self.context_menu.add_command(label="Удалить", command=self.delete_entry)
        self.context_menu.configure(
            background="gray24",
            foreground="sea green",
            font=('Helvetica', 12)
        )
        self.entry_frame.bind("<Button-3>", self.show_context_menu)

        # Поля с данными записи.
        label_service_name = ttk.Label(
            self.entry_frame,
            text=self.service_name
        )
        label_service_name.bind("<Button-3>", self.show_context_menu)
        label_service_name.pack(
            anchor="nw",
            padx=8,
            pady=2
        )
        label_login = ttk.Label(
            self.entry_frame,
            text=self.login,
            font=('Helvetica', 10)
        )
        label_login.bind("<Button-3>", self.show_context_menu)
        label_login.pack(
            anchor="sw",
            padx=8,
            pady=4
        )

    def show_context_menu(self, event) -> None:
        """Вызов контекстного меню."""

        self.context_menu.post(event.x_root, event.y_root)

    def copy_password(self) -> None:
        """Копирует пароль в буфер обмена."""

        self.entry_frame.clipboard_clear()
        self.entry_frame.clipboard_append(self.pm.encryption.decrypt(self.encrypted_password))

    def delete_entry(self) -> None:
        """Удаляет запись из БД и списка записей."""

        self.pm.db.delete_entry(self.entry_id)
        self.entry_frame.destroy()
        self.pm.page_entry_list.list_show_page(1)

    def update_entry(self) -> None:
        """Переход на страницу редактирования записи."""

        self.pm.page_add_or_update.entry_id = self.entry_id
        self.pm.page_add_or_update.mode_update(self.service_name, self.login)
        self.pm.page_entry_list.hide()
        self.pm.page_add_or_update.show()

    def add_entry(self) -> None:
        """Переход на страницу создания записи."""

        self.pm.page_add_or_update.mode_add()
        self.pm.page_entry_list.hide()
        self.pm.page_add_or_update.show()


class PageRequestPassword:
    """
    Страница ввода мастер-пароля.
    Реализует создание и проверку мастер-пароля.
    """

    def __init__(self, pm: PasswordManager):

        # Главный класс приложения.
        self.pm = pm

        # Контейнер поля ввода пароля.
        self.password_frame = ttk.Labelframe(
            self.pm.root,
            labelanchor="nw",
            text=" Введите мастер-пароль ",
        )

        # Поле ввода пароля.
        self.password_entry = ttk.Entry(
            self.password_frame,
            cursor="draft_large",
            font=('Helvetica', 14),
            justify="left"
        )

        self.hint_label = ttk.Label(
            self.password_frame,
            justify="left",
            text="Придумайте мастер-пароль. \nОн будет использоваться \nдля доступа к паролям для \nваших учетных "
                 "записей, \nсгенерированным \nприложением. \n\nВнимание!\nПри потере пароля доступ к "
                 "\nданным будет невозможен!"
        )

        if not self.pm.db.is_empty():
            self.hint_label.configure(
                text="Введите мастер-пароль."
            )

        # Сообщение об ошибке.
        self.error_label = ttk.Label(
            self.password_frame,
            foreground="red",
            justify="left"
        )

        # Контейнер кнопок.
        self.button_frame = ttk.Frame(
            self.pm.root
        )

        # Кнопка сохранения пароля.
        self.add_button = ttk.Button(
            self.button_frame,
            command=self.enter_password,
            width=10,
            text="Ок"
        )

    def show(self) -> None:
        """Отображает виджеты страницы."""

        self.password_frame.pack(
            expand=True,
            fill="both",
            padx=12,
            pady=(12, 0)
        )
        self.password_entry.pack(
            anchor="nw",
            fill="x",
            expand=False,
            pady=6
        )
        self.hint_label.pack(
            expand=False,
            anchor="n",
            side="left",
            padx=6,
            pady=6
        )
        self.button_frame.pack(
            expand=False,
            fill="x",
            padx=12,
            pady=12
        )
        self.add_button.pack(
            anchor="center",
            padx=12,
            pady=12
        )

    def hide(self) -> None:
        """Скрывает виджеты страницы."""

        self.password_frame.pack_forget()
        self.button_frame.pack_forget()

    def enter_password(self) -> None:
        """Проверяет мастер-пароль и создает шифровщик."""

        # Получение пароля.
        password = self.password_entry.get()
        self.pm.encryption = PasswordEncryption(password)

        # Проверка пароля.
        if not self.pm.db.is_empty():
            try:
                self.pm.encryption.decrypt(self.pm.db.get_all()[0][3])
            except InvalidToken:
                self.error_label.configure(text="Неправильный пароль.")
                self.error_label.pack(side="top")
                self.hint_label.pack_configure(after=self.error_label)
                return
        elif password == "":
            self.error_label.configure(text="Недопустимый пароль.")
            self.error_label.pack(side="top")
            self.hint_label.pack_configure(after=self.error_label)
            return

        # Переход на страницу списка.
        self.hide()
        self.pm.page_entry_list.show()


class PageAddOrUpdate:
    """
    Страница создания и редактирования записи.
    """

    def __init__(self, pm: PasswordManager):

        # Главный класс приложения.
        self.pm = pm

        # Номер изменяемой записи.
        self.entry_id = 0

        # Переменные для полей ввода.
        self.service_name_entry_var = tk.StringVar()
        self.login_entry_var = tk.StringVar()

        # Контейнер полей ввода.
        self.input_frame = ttk.Labelframe(
            self.pm.root,
            labelanchor="nw"
        )

        # Заголовок поля ввода названия сервиса.
        self.service_name_label = ttk.Label(
            self.input_frame,
            font=('Helvetica', 14),
            justify="left",
            text="Название сервиса:"
        )

        # Поле ввода названия сервиса.
        self.service_name_entry = ttk.Entry(
            self.input_frame,
            textvariable=self.service_name_entry_var,
            font=('Helvetica', 14),
            justify="left"
        )

        # Заголовок поля ввода логина.
        self.login_label = ttk.Label(
            self.input_frame,
            font=('Helvetica', 14),
            justify="left",
            text="Логин:"
        )

        # Поле ввода логина.
        self.login_entry = ttk.Entry(
            self.input_frame,
            textvariable=self.login_entry_var,
            font=('Helvetica', 14),
            justify="left"
        )

        # Контейнер кнопок.
        self.button_frame = ttk.Frame(
            self.pm.root
        )

        # Кнопка сохранения изменений.
        self.add_button = ttk.Button(
            self.button_frame,
            width=10,
            text="Ок"
        )

        # Кнопка отмены изменений.
        self.cancel_button = ttk.Button(
            self.button_frame,
            command=self.go_back,
            width=10,
            text="Отмена"
        )

    def show(self) -> None:
        """Отображает виджеты страницы."""

        self.input_frame.pack(
            expand=True,
            fill="both",
            padx=12,
            pady=(12, 0)
        )
        self.service_name_label.pack(
            anchor="nw",
            pady=(24, 0)
        )
        self.service_name_entry.pack(
            anchor="nw",
            fill="x",
            expand=False,
            pady=(2, 0)
        )
        self.login_label.pack(
            anchor="nw",
            pady=(24, 0)
        )
        self.login_entry.pack(
            anchor="nw",
            fill="x",
            expand=False,
            pady=(2, 0)
        )
        self.button_frame.pack(
            expand=False,
            fill="x",
            padx=12,
            pady=12
        )
        self.add_button.pack(
            anchor="center",
            side="left",
            padx=12,
            pady=12
        )
        self.cancel_button.pack(
            anchor="center",
            side="right",
            padx=12,
            pady=12
        )

    def hide(self) -> None:
        """Скрывает виджеты страницы."""

        self.input_frame.pack_forget()
        self.button_frame.pack_forget()

    def mode_update(self, service_name: str, login: str) -> None:
        """Переключить виджеты на изменение записи."""

        self.input_frame.configure(
            text=" Изменить запись "
        )
        self.add_button.configure(
            command=self.update_entry
        )
        self.service_name_entry_var.set(service_name)
        self.login_entry_var.set(login)

    def mode_add(self) -> None:
        """Переключить виджеты на создание записи."""

        self.input_frame.configure(
            text=" Добавить запись "
        )
        self.add_button.configure(
            command=self.add_entry
        )
        self.service_name_entry_var.set("")
        self.login_entry_var.set("")

    def go_back(self) -> None:
        """Возвращает на страницу списка."""

        self.hide()
        self.pm.page_entry_list.show()

    def add_entry(self) -> None:
        """Создает запись с данными из полей ввода."""

        # Добавление записи в БД.
        self.pm.db.add_entry(
            self.service_name_entry_var.get(),
            self.login_entry_var.get(),
            self.pm.encryption.encrypt(generate_password())
        )

        # Возврат на страницу списка.
        self.pm.page_entry_list.list_show_page(1)
        self.go_back()

    def update_entry(self) -> None:
        """Изменяет выбранную запись данными из полей ввода."""

        # Обновление записи в БД.
        self.pm.db.update_entry(
            self.entry_id,
            self.service_name_entry_var.get(),
            self.login_entry_var.get()
        )

        # Возврат на страницу списка.
        self.pm.page_entry_list.list_show_page(1)
        self.go_back()
