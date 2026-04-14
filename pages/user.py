from top_labels.top_level import *
import customtkinter as ctk
from tkinter import filedialog


class UsersPage(ctk.CTkFrame):
    def __init__(self, parent, db, controller):
        super().__init__(parent)
        self.db = db
        self.controller = controller

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.users_page()

    def users_page(self):
        container = ctk.CTkFrame(self, fg_color=cons.BG)
        container.grid(row=1, column=0, sticky="nsew")

        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(1, weight=1)

        # 🔹 HEADER
        header = ctk.CTkFrame(container, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=10)

        title = ctk.CTkLabel(header, text="Users", font=("Arial", 20, "bold"))
        title.pack(side="left")

        # кнопки справа
        btn_frame = ctk.CTkFrame(header, fg_color="transparent")
        btn_frame.pack(side="right")

        add_btn = ctk.CTkButton(btn_frame, text="Add", width=80)
        add_btn.pack(side="left", padx=5)

        delete_btn = ctk.CTkButton(btn_frame, text="Delete", width=80)
        delete_btn.pack(side="left", padx=5)

        export_btn = ctk.CTkButton(
            btn_frame,
            text="Export",
            width=80,
            command=self.export_users
        )
        export_btn.pack(side="left", padx=5)

        # 🔹 СПИСОК ПОЛЬЗОВАТЕЛЕЙ (scroll)
        users_frame = ctk.CTkScrollableFrame(container)
        users_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)

        # 🔹 пример данных (потом заменишь на db)
        users = ["Murat", "Ali", "Bek", "Azamat", "Nursultan"]

        for user in users:
            card = ctk.CTkFrame(users_frame, corner_radius=10)
            card.pack(fill="x", pady=5)

            name = ctk.CTkLabel(card, text=user, font=("Arial", 14))
            name.pack(side="left", padx=10, pady=10)

            edit_btn = ctk.CTkButton(card, text="Edit", width=70)
            edit_btn.pack(side="right", padx=5)

            view_btn = ctk.CTkButton(card, text="View", width=70)
            view_btn.pack(side="right", padx=5)

    def export_users(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[
                ("Text files", "*.txt"),
                ("CSV files", "*.csv")
            ]
        )

        if file_path:
            users = ["Murat", "Ali", "Bek"]

            with open(file_path, "w", encoding="utf-8") as f:
                for user in users:
                    f.write(user + "\n")