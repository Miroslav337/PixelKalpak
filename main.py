import customtkinter as ctk
from PIL import Image
import constantes as cons
from database import LibraryDB
from pages import MainPage, CatalogPage, AdminPage, UsersPage, LogInPage, ProfilePage

ctk.set_appearance_mode("light")



class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.db = LibraryDB()
        self.geometry("1200x720")
        self.configure(fg_color=cons.BG)
        self.title("Library")
        self.is_logged_in = False

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.load_resources()

        self.topbar()

        container = ctk.CTkFrame(self)
        container.grid(row=1, column=0, sticky="nsew")
        container.grid_rowconfigure(1, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.pages = {}

        for Page in (MainPage, CatalogPage, UsersPage, AdminPage, LogInPage, ProfilePage):
            page = Page(container, self.db, self)
            self.pages[Page] = page

            page.grid(row=1, column=0, sticky="nsew")

        self.show_page(MainPage)

    def load_resources(self):
        """Загрузка всех изображений один раз при старте"""
        self.logo_img = ctk.CTkImage(light_image=Image.open("image/logo.jpg"), size=(40, 40))
        self.img_normal = ctk.CTkImage(light_image=Image.open("image/login.png"), size=(13, 13))
        self.img_hover = ctk.CTkImage(light_image=Image.open("image/logo.jpg"), size=(13, 13))

    def topbar(self):
        header = ctk.CTkFrame(self, height=60, fg_color=cons.CARD, corner_radius=15)
        header.grid(row=0, column=0, sticky="ew", padx=10, pady=10)

        header.grid_columnconfigure(0, weight=0)
        header.grid_columnconfigure(1, weight=30)
        header.grid_columnconfigure(2, weight=10)
        header.grid_columnconfigure(3, weight=0)

        logo_label = ctk.CTkLabel(header, image=self.logo_img, text="")
        logo_label.grid(row=0, column=0, padx=15, sticky="w")
        # logo = ctk.CTkButton(header, image=self.logo_img, compound="top")
        # logo.grid(row=0, column=0, padx=15, sticky="w")

        pixel = ctk.CTkLabel(header, text="Pixel Kalpak", font=("Arial", 20))
        pixel.grid(row=0, column=1, padx=10, pady=(10, 5), sticky="w")

        self.nav_frame = ctk.CTkFrame(header, fg_color="transparent")
        self.nav_frame.grid(row=0, column=2, sticky="ew")

        self.login_container = ctk.CTkFrame(header, fg_color="transparent")
        self.login_container.grid(row=0, column=3, padx=5, sticky="ew")

        self.update_login_button()

    def update_navigation(self, current_page_class):
        for widget in self.nav_frame.winfo_children():
            widget.destroy()

        buttons_data = [
            ("main page", MainPage),
            ("catalog page", CatalogPage),
            ("admin", AdminPage),
            ("users", UsersPage),
        ]

        column_index = 0
        for text, page_class in buttons_data:
            if page_class == current_page_class:
                self.nav_frame.grid_columnconfigure(column_index, weight=1)
                btn = ctk.CTkButton(
                    self.nav_frame,
                    text=text,
                    fg_color="transparent",
                    text_color=cons.BLUE_ACTIVE,
                    command=lambda p=page_class: self.show_page(p)
                )
                btn.grid(row=0, column=column_index, padx=5, sticky="ew")
                column_index += 1
            else:
                self.nav_frame.grid_columnconfigure(column_index, weight=1)
                btn = ctk.CTkButton(
                    self.nav_frame,
                    text=text,
                    fg_color="transparent",
                    text_color="black",
                    hover_color=cons.GRAY,
                    command=lambda p=page_class: self.show_page(p)
                )
                btn.grid(row=0, column=column_index, padx=5, sticky="ew")
                column_index += 1

    def show_page(self, page_class):
        self.pages[page_class].tkraise()
        self.update_navigation(page_class)

    def update_login_button(self):
        for widget in self.login_container.winfo_children():
            widget.destroy()

        if not self.is_logged_in:
            self.login = ctk.CTkButton(
                self.login_container, text="log in", image=self.img_normal,
                compound="right", width=100, border_spacing=10,
                fg_color=cons.BLUE, text_color="black", hover_color=cons.BLUE_ACTIVE,
                command=lambda: self.show_page(LogInPage)
            )
        else:
            self.login = ctk.CTkButton(
                self.login_container, text="Profile", image=self.img_normal,
                compound="right", width=100, border_spacing=10,
                fg_color=cons.ACCENT, text_color="black", hover_color=cons.GRAY,
                command=lambda: self.show_page(ProfilePage)
            )

        self.login.pack(fill="both", expand=True)
        self.login.bind("<Enter>", self.on_enter)
        self.login.bind("<Leave>", self.on_leave)

    def set_authorized(self):
        self.is_logged_in = True
        self.update_login_button()
        self.show_page(MainPage)

    def set_logged_out(self):
        """бесполезный метод для проверки"""
        self.is_logged_in = False
        self.update_login_button()
        self.show_page(MainPage)

    def on_enter(self, event):
        self.login.configure(image=self.img_hover)

    def on_leave(self, event):
        self.login.configure(image=self.img_normal)

if __name__ == "__main__":
    app = App()
    app.mainloop()