import customtkinter as ctk
from PIL import Image
import constantes as cons

class LogInPage(ctk.CTkFrame):
    def __init__(self, parent, db, controller):
        super().__init__(parent)
        self.db = db
        self.controller = controller

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.login_page()

    def login_page(self):
        container = ctk.CTkFrame(self, fg_color=cons.BG)
        container.grid(row=1, column=0, sticky="nsew")

        container.grid_columnconfigure((1, 2, 3, 4), weight=10)
        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(2, weight=1)

        label = ctk.CTkLabel(container, text="log in", font=("Arial", 14))
        label.grid(row=0, column=0, sticky="nsew")

        btn_login = ctk.CTkButton(
            container,
            text="Имитировать Вход",
            command=self.controller.set_authorized  # Вызываем метод в App
        )
        btn_login.grid(row=1, column=0, sticky="nsew")

class ProfilePage(ctk.CTkFrame):
    def __init__(self, parent, db, controller):
        super().__init__(parent)
        self.db = db
        self.controller = controller

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.profile_page()

    def profile_page(self):
        container = ctk.CTkFrame(self, fg_color=cons.BG)
        container.grid(row=1, column=0, sticky="nsew")

        container.grid_columnconfigure((1, 2, 3, 4), weight=10)
        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(2, weight=1)

        label = ctk.CTkLabel(container, text="profile", font=("Arial", 14))
        label.grid(row=0, column=0, sticky="nsew")

        btn_logout = ctk.CTkButton(
            container,
            text="Выйти из аккаунта",
            fg_color="red",
            command=self.controller.set_logged_out
        )
        btn_logout.grid(row=1, column=0, sticky="nsew")