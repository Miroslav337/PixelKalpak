from top_labels.top_level import *

class UsersPage(ctk.CTkFrame):
    def __init__(self, parent, db):
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

    def open_settings(self):
        if self.settings_window is None or not self.settings_window.winfo_exists():
            self.settings_window = tl(self.winfo_toplevel())
        else:
            self.settings_window.focus()