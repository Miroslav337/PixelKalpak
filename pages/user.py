from top_labels.top_level import *
from tkinter import filedialog
import customtkinter as ctk

class UsersPage(ctk.CTkFrame):
    def __init__(self, parent, db, controller):
        super().__init__(parent)
        self.db = db

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.users_page()

    def users_page(self):
        container = ctk.CTkFrame(self, fg_color=cons.BG)
        container.grid(row=1, column=0, sticky="nsew")

        container.grid_columnconfigure((1, 2, 3, 4), weight=10)
        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(2, weight=1)

        label = ctk.CTkLabel(container, text="users", font=("Arial", 14))
        label.grid(row=0, column=0, sticky="nsew")

    def users_page(self):
        container = ctk.CTkFrame(self, fg_color=cons.BG)
        container.grid(row=1, column=0, sticky="nsew")

        container.grid_columnconfigure((1, 2, 3, 4), weight=10)
        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(2, weight=1)

        label = ctk.CTkLabel(container, text="users", font=("Arial", 14))
        label.grid(row=0, column=0, sticky="w", padx=10)

        # 🔹 КНОПКА EXPORT
        export_btn = ctk.CTkButton(
            container,
            text="Export files",
            command=self.export_users
        )
        export_btn.grid(row=0, column=4, sticky="e", padx=10, pady=10)

    def export_users(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[
                ("Text files", "*.txt"),
                ("CSV files", "*.csv")
            ]
        )

        if file_path:
            # 🔹 пример данных (замени на свои)
            users = ["Murat", "Ali", "Bek"]

            with open(file_path, "w", encoding="utf-8") as f:
                for user in users:
                    f.write(user + "\n")


    def open_settings(self):
        if self.settings_window is None or not self.settings_window.winfo_exists():
            self.settings_window = (self.winfo_toplevel())
        else:
            self.settings_window.focus()