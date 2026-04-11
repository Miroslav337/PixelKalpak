from .top_level import TopLevel
import customtkinter as ctk


class AddBook(TopLevel):
    def __init__(self, master):
        super().__init__(master, title="Добавить книгу", width=350, height=400)
        ctk.CTkLabel(self.main_frame, text="Новая книга", font=("Arial", 16)).pack(pady=10)

        self.entry = ctk.CTkEntry(self.main_frame, placeholder_text="Название книги")
        self.entry.pack(pady=10, padx=20, fill="x")

        ctk.CTkButton(self.main_frame, text="Сохранить", command=self.on_close).pack(pady=20)


class DeleteBook(TopLevel):
    def __init__(self, master):
        super().__init__(master, title="Удалить", width=300, height=180)
        ctk.CTkLabel(self.main_frame, text="Удалить выбранную книгу?", wraplength=250).pack(pady=20)

        btn_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        btn_frame.pack(pady=10)

        ctk.CTkButton(btn_frame, text="Да", width=80, command=self.on_close).grid(row=0, column=0, padx=5)
        ctk.CTkButton(btn_frame, text="Нет", width=80, command=self.on_close).grid(row=0, column=1, padx=5)

class EditUser(TopLevel):
    def __init__(self, master):
        super().__init__(master, title="Редактировать юзера")

class SystemLogs(TopLevel):
    def __init__(self, master):
        super().__init__(master, title="Логи системы", width=500, height=400)