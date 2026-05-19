import os
import customtkinter as ctk
from PIL import Image
import constantes as cons
from database import LibraryDB
from i18n import I18n
from settings import AppSettings, ACCENT_PRESETS
from pages import MainPage, CatalogPage, UsersPage, LogInPage, ProfilePage

_HERE = os.path.dirname(os.path.abspath(__file__))


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.settings = AppSettings()
        ctk.set_appearance_mode(self.settings.theme)
        self._apply_palette(self.settings.theme)
        colors = ACCENT_PRESETS[self.settings.accent]
        cons.BLUE = colors["BLUE"]
        cons.BLUE_ACTIVE = colors["BLUE_ACTIVE"]
        cons.ACCENT = colors["ACCENT"]

        self.db = LibraryDB(os.path.join(_HERE, "library.db"))
        self.i18n = I18n(lang=self.settings.language)
        self.geometry("1200x720")
        self.minsize(900, 600)
        self.configure(fg_color=cons.BG)
        self.title("Pixel Kalpak")
        self.is_logged_in = False
        self.current_admin = None
        self._current_page = MainPage

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.load_resources()
        self.topbar()

        self._container = ctk.CTkFrame(self, fg_color=cons.BG)
        self._container.grid(row=1, column=0, sticky="nsew")
        self._container.grid_rowconfigure(1, weight=1)
        self._container.grid_columnconfigure(0, weight=1)

        self.pages = {}
        for Page in (MainPage, CatalogPage, UsersPage, LogInPage, ProfilePage):
            page = Page(self._container, self.db, self.i18n, self)
            self.pages[Page] = page
            page.grid(row=1, column=0, sticky="nsew")

        self.show_page(MainPage)

    # ─────────────────────────── RESOURCES ─────────────────────────

    def load_resources(self):
        img_dir = os.path.join(_HERE, "image")
        self.logo_img = ctk.CTkImage(light_image=Image.open(os.path.join(img_dir, "logo.png")), size=(50, 35))
        self.img_normal = ctk.CTkImage(light_image=Image.open(os.path.join(img_dir, "login.png")), size=(13, 13))
        self.img_hover = ctk.CTkImage(light_image=Image.open(os.path.join(img_dir, "login.png")), size=(13, 13))

    # ─────────────────────────── PALETTE ───────────────────────────

    def _apply_palette(self, theme: str):
        palette = cons.DARK_COLORS if theme == "dark" else cons.LIGHT_COLORS
        cons.BG   = palette["BG"]
        cons.CARD = palette["CARD"]
        cons.GRAY = palette["GRAY"]
        cons.TEXT = palette["TEXT"]

    # ─────────────────────────── TOPBAR ────────────────────────────

    def topbar(self):
        self.topbar_frame = ctk.CTkFrame(self, height=56, fg_color=cons.CARD, corner_radius=14)
        self.topbar_frame.grid(row=0, column=0, sticky="ew", padx=12, pady=(10, 6))
        self.topbar_frame.grid_propagate(False)
        self.topbar_frame.grid_rowconfigure(0, weight=1)  # vertically center all children

        self.topbar_frame.grid_columnconfigure(0, weight=0)  # logo
        self.topbar_frame.grid_columnconfigure(1, weight=1)  # title (expands)
        self.topbar_frame.grid_columnconfigure(2, weight=0)  # nav (near login)
        self.topbar_frame.grid_columnconfigure(3, weight=0)  # login btn

        # Logo
        ctk.CTkLabel(self.topbar_frame, image=self.logo_img, text="").grid(
            row=0, column=0, padx=(16, 8)
        )

        # Title
        ctk.CTkLabel(
            self.topbar_frame, text="Pixel Kalpak",
            font=("Arial", 18, "bold"), text_color=cons.TEXT,
        ).grid(row=0, column=1, padx=(0, 16), sticky="w")

        # Nav area
        self.nav_frame = ctk.CTkFrame(self.topbar_frame, fg_color="transparent")
        self.nav_frame.grid(row=0, column=2)

        # Login/Profile button
        self.login_container = ctk.CTkFrame(self.topbar_frame, fg_color="transparent")
        self.login_container.grid(row=0, column=3, padx=(4, 12))

        self.update_login_button()

    def update_navigation(self, current_page_class):
        for widget in self.nav_frame.winfo_children():
            widget.destroy()

        buttons_data = [
            (self.i18n.t("nav.main"),    MainPage),
            (self.i18n.t("nav.catalog"), CatalogPage),
            (self.i18n.t("nav.users"),   UsersPage),
        ]

        is_dark = self.settings.theme == "dark"
        for col, (text, page_class) in enumerate(buttons_data):
            self.nav_frame.grid_columnconfigure(col, weight=1)
            is_active = page_class == current_page_class
            # in dark mode use BLUE_ACTIVE (darker) as pill so white text has better contrast
            pill = (cons.BLUE_ACTIVE if is_dark else cons.BLUE) if is_active else "transparent"
            btn = ctk.CTkButton(
                self.nav_frame,
                text=text,
                height=34,
                corner_radius=8,
                fg_color=pill,
                text_color=cons.TEXT,
                hover_color=cons.GRAY,
                font=("Arial", 13, "bold") if is_active else ("Arial", 13),
                command=lambda p=page_class: self.show_page(p),
            )
            btn.grid(row=0, column=col, padx=4, sticky="ew")

    def update_login_button(self):
        for widget in self.login_container.winfo_children():
            widget.destroy()

        if not self.is_logged_in:
            self.login = ctk.CTkButton(
                self.login_container,
                text=self.i18n.t("btn.login"),
                image=self.img_normal, compound="right",
                width=110, height=36, corner_radius=8, border_spacing=10,
                fg_color=cons.BLUE, text_color=cons.TEXT, hover_color=cons.BLUE_ACTIVE,
                command=lambda: self.show_page(LogInPage),
            )
        else:
            self.login = ctk.CTkButton(
                self.login_container,
                text=self.i18n.t("page.profile"),
                image=self.img_normal, compound="right",
                width=110, height=36, corner_radius=8, border_spacing=10,
                fg_color=cons.BLUE, text_color=cons.TEXT, hover_color=cons.BLUE_ACTIVE,
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
        self.configure(fg_color=cons.BG)
        self._container.configure(fg_color=cons.BG)
        self.topbar_frame.destroy()
        self.topbar()
        for page in self.pages.values():
            page.configure(fg_color=cons.BG)
            page.rebuild()
        self.update_navigation(self._current_page)
        self.update_login_button()


if __name__ == "__main__":
    app = App()
    app.mainloop()
