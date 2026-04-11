import customtkinter as ctk
from PIL import Image
import constantes as cons
from top_labels import AddBook

class AdminPage(ctk.CTkFrame):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.admin_page()

    def admin_page(self):
        container = ctk.CTkFrame(self, fg_color=cons.BG)
        container.grid(row=1, column=0, sticky="nsew")

        container.grid_columnconfigure((1, 2, 3, 4), weight=10)
        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(2, weight=1)

        label = ctk.CTkLabel(container, text="admin", font=("Arial", 14))
        label.grid(row=0, column=0, sticky="nsew")

        btn_add = (ctk.CTkButton(container, text="Добавить", command=lambda: self.open_popup("add_window", AddBook)))
        btn_add.grid(row=1, column=0, sticky="nsew")

    def open_popup(self, attr_name, popup_class):
        current_window = getattr(self, attr_name, None)

        if current_window is None or not current_window.winfo_exists():
            new_window = popup_class(self.winfo_toplevel())
            setattr(self, attr_name, new_window)
        else:
            current_window.focus()