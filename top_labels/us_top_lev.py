from .top_level import TopLevel
import customtkinter as ctk


class UserInfo(TopLevel):
    def __init__(self, master):
        super().__init__(master, title="Инфо", width=300, height=150)

        ctk.CTkLabel(self.main_frame, text="Вы вошли как: Guest", font=("Arial", 14)).pack(pady=20)
        ctk.CTkButton(self.main_frame, text="OK", command=self.on_close, width=100).pack()