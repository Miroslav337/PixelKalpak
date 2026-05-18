import os
import customtkinter as ctk
from PIL import Image
import constantes as cons
from database import LibraryDB
from locale import I18n
from settings import AppSettings, ACCENT_PRESETS
from pages import MainPage, CatalogPage, UsersPage, LogInPage, ProfilePage

_HERE = os.path.dirname(os.path.abspath(__file__))


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.settings = AppSettings()
        ctk.set_appearance_mode(self.settings.theme)
        colors = ACCENT_PRESETS[self.settings.accent]
        cons.BLUE = colors["BLUE"]
        cons.BLUE_ACTIVE = colors["BLUE_ACTIVE"]
        cons.ACCENT = colors["ACCENT"]

        self.db = LibraryDB(os.path.join(_HERE, "library.db"))
        self.i18n = I18n(lang=self.settings.language)
        self.geometry("1200x720")
        self.minsize(900, 600)
        self.configure(fg_color=cons.BG)
        self.title("Library")
        self.is_logged_in = False
        self.current_admin = None
        self._current_page = MainPage

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.load_resources()
        self.topbar()

        container = ctk.CTkFrame(self)
        container.grid(row=1, column=0, sticky="nsew")
        container.grid_rowconfigure(1, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.pages = {}
        for Page in (MainPage, CatalogPage, UsersPage, LogInPage, ProfilePage):
            page = Page(container, self.db, self.i18n, self)
            self.pages[Page] = page
            page.grid(row=1, column=0, sticky="nsew")

        self.show_page(MainPage)

    # ─────────────────────────── RESOURCES ─────────────────────────

    def load_resources(self):
        img_dir = os.path.join(_HERE, "image")
        self.logo_img = ctk.CTkImage(light_image=Image.open(os.path.join(img_dir, "logo.png")), size=(50, 35))
        self.img_normal = ctk.CTkImage(light_image=Image.open(os.path.join(img_dir, "login.png")), size=(13, 13))
        self.img_hover = ctk.CTkImage(light_image=Image.open(os.path.join(img_dir, "login.png")), size=(13, 13))

    # ─────────────────────────── TOPBAR ────────────────────────────

    def topbar(self):
        self.topbar_frame = ctk.CTkFrame(self, height=60, fg_color=cons.CARD, corner_radius=15)
        self.topbar_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)

        self.topbar_frame.grid_columnconfigure(0, weight=0)
        self.topbar_frame.grid_columnconfigure(1, weight=30)
        self.topbar_frame.grid_columnconfigure(2, weight=10)
        self.topbar_frame.grid_columnconfigure(3, weight=0)

        ctk.CTkLabel(self.topbar_frame, image=self.logo_img, text="").grid(
            row=0, column=0, padx=15, sticky="w"
        )
        ctk.CTkLabel(self.topbar_frame, text="Pixel Kalpak", font=("Arial", 20)).grid(
            row=0, column=1, padx=10, pady=(10, 5), sticky="w"
        )

        self.nav_frame = ctk.CTkFrame(self.topbar_frame, fg_color="transparent")
        self.nav_frame.grid(row=0, column=2, sticky="ew")

        self.login_container = ctk.CTkFrame(self.topbar_frame, fg_color="transparent")
        self.login_container.grid(row=0, column=3, padx=5, sticky="ew")

        self.update_login_button()

    def update_navigation(self, current_page_class):
        for widget in self.nav_frame.winfo_children():
            widget.destroy()

        buttons_data = [
            (self.i18n.t("nav.main"),     MainPage),
            (self.i18n.t("nav.catalog"),  CatalogPage),
            (self.i18n.t("nav.users"),    UsersPage),
        ]

        for col, (text, page_class) in enumerate(buttons_data):
            self.nav_frame.grid_columnconfigure(col, weight=1)
            is_active = page_class == current_page_class
            btn = ctk.CTkButton(
                self.nav_frame,
                text=text,
                fg_color="transparent",
                text_color=cons.BLUE_ACTIVE if is_active else "black",
                hover_color=cons.GRAY,
                command=lambda p=page_class: self.show_page(p),
            )
            btn.grid(row=0, column=col, padx=5, sticky="ew")

    def update_login_button(self):
        for widget in self.login_container.winfo_children():
            widget.destroy()

        if not self.is_logged_in:
            self.login = ctk.CTkButton(
                self.login_container,
                text=self.i18n.t("btn.login"),
                image=self.img_normal, compound="right",
                width=100, border_spacing=10,
                fg_color=cons.BLUE, text_color="black", hover_color=cons.BLUE_ACTIVE,
                command=lambda: self.show_page(LogInPage),
            )
        else:
            self.login = ctk.CTkButton(
                self.login_container,
                text=self.i18n.t("page.profile"),
                image=self.img_normal, compound="right",
                width=100, border_spacing=10,
                fg_color=cons.ACCENT, text_color="black", hover_color=cons.GRAY,
                command=lambda: self.show_page(ProfilePage),
            )

        self.login.pack(fill="both", expand=True)
        self.login.bind("<Enter>", self.on_enter)
        self.login.bind("<Leave>", self.on_leave)

    def on_enter(self, event):
        self.login.configure(image=self.img_hover)

    def on_leave(self, event):
        self.login.configure(image=self.img_normal)

    # ─────────────────────────── NAVIGATION ────────────────────────

    def show_page(self, page_class):
        self._current_page = page_class
        self.pages[page_class].tkraise()
        self.update_navigation(page_class)

    # ─────────────────────────── AUTH ──────────────────────────────

    def set_authorized(self, admin: dict):
        self.current_admin = admin
        self.is_logged_in = True
        self.pages[ProfilePage].refresh()
        self.pages[CatalogPage].refresh()
        self.pages[UsersPage].refresh()
        self.update_login_button()
        self.show_page(MainPage)

    def set_logged_out(self):
        self.current_admin = None
        self.is_logged_in = False
        self.pages[ProfilePage].refresh()
        self.pages[CatalogPage].refresh()
        self.pages[UsersPage].refresh()
        self.update_login_button()
        self.show_page(MainPage)

    # ─────────────────────────── SETTINGS ──────────────────────────

    def apply_accent(self, preset_name: str):
        colors = ACCENT_PRESETS[preset_name]
        cons.BLUE = colors["BLUE"]
        cons.BLUE_ACTIVE = colors["BLUE_ACTIVE"]
        cons.ACCENT = colors["ACCENT"]
        self.topbar_frame.destroy()
        self.topbar()
        self.update_navigation(self._current_page)

    def rebuild_ui(self):
        for page in self.pages.values():
            page.rebuild()
        self.update_navigation(self._current_page)
        self.update_login_button()


if __name__ == "__main__":
    app = App()
    app.mainloop()
