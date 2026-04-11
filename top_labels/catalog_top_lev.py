from .top_level import TopLevel
import customtkinter as ctk


class CatalogBookInfo(TopLevel):
    def __init__(self, master):
        super().__init__(master, title="Фильтры", width=300, height=250)

        ctk.CTkLabel(self.main_frame, text="Настройка фильтров", font=("Arial", 16, "bold")).pack(pady=10)

        self.check = ctk.CTkCheckBox(self.main_frame, text="Только в наличии")
        self.check.pack(pady=10)

        ctk.CTkButton(self.main_frame, text="Применить", command=self.on_close).pack(pady=10)