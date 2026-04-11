import customtkinter as ctk
from PIL import Image
import constantes as cons

class LogInPage(ctk.CTkFrame):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db

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