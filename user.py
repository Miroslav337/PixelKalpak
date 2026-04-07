import customtkinter as ctk
from PIL import Image

class UsersPage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.users_page()

    def users_page(self):
        ctk.CTkLabel(self, text="users", font=("Arial", 14)).pack(pady=10)