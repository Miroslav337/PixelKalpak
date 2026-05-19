from .top_level import TopLevel
import customtkinter as ctk
import constantes as cons


class AddBook(TopLevel):
    def __init__(self, master, db, i18n, refresh_callback):
        super().__init__(master, title=i18n.t("popup.add_book"), width=420, height=500)
        self.db = db
        self.i18n = i18n
        self.refresh_callback = refresh_callback
        self._build()

    def _build(self):
        # Title bar
        title_bar = ctk.CTkFrame(self.main_frame, fg_color=cons.BLUE_ACTIVE, corner_radius=0, height=40)
        title_bar.pack(fill="x")
        title_bar.pack_propagate(False)
        ctk.CTkLabel(
            title_bar, text=self.i18n.t("popup.add_book"),
            font=("Arial", 14, "bold"), text_color="black"
        ).pack(side="left", padx=12, pady=8)
        ctk.CTkButton(
            title_bar, text="✕", width=32, height=28,
            fg_color="transparent", hover_color="#d95050", text_color="white",
            command=self.on_close
        ).pack(side="right", padx=4, pady=4)

        # Form
        form = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=24, pady=12)
        form.grid_columnconfigure(0, weight=1)

        vcmd = (self.register(lambda v: v == "" or v.isdigit()), "%P")

        # Title (required)
        ctk.CTkLabel(form, text=self.i18n.t("label.title") + " *", anchor="w").grid(
            row=0, column=0, sticky="w"
        )
        self.title_entry = ctk.CTkEntry(form)
        self.title_entry.grid(row=1, column=0, sticky="ew", pady=(2, 8))

        # Author
        ctk.CTkLabel(form, text=self.i18n.t("label.author"), anchor="w").grid(
            row=2, column=0, sticky="w"
        )
        self.author_entry = ctk.CTkEntry(form)
        self.author_entry.grid(row=3, column=0, sticky="ew", pady=(2, 8))

        # Publisher
        ctk.CTkLabel(form, text=self.i18n.t("label.publisher"), anchor="w").grid(
            row=4, column=0, sticky="w"
        )
        self.publisher_entry = ctk.CTkEntry(form)
        self.publisher_entry.grid(row=5, column=0, sticky="ew", pady=(2, 8))

        # Year + Count (side by side)
        row_frame = ctk.CTkFrame(form, fg_color="transparent")
        row_frame.grid(row=6, column=0, sticky="ew", pady=(0, 8))
        row_frame.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(row_frame, text=self.i18n.t("label.year"), anchor="w").grid(
            row=0, column=0, sticky="w"
        )
        self.year_entry = ctk.CTkEntry(row_frame, validate="key", validatecommand=vcmd)
        self.year_entry.grid(row=1, column=0, sticky="ew", padx=(0, 6))

        ctk.CTkLabel(row_frame, text=self.i18n.t("label.count"), anchor="w").grid(
            row=0, column=1, sticky="w"
        )
        self.count_entry = ctk.CTkEntry(row_frame, validate="key", validatecommand=vcmd)
        self.count_entry.insert(0, "1")
        self.count_entry.grid(row=1, column=1, sticky="ew", padx=(6, 0))

        # Genres
        ctk.CTkLabel(form, text=self.i18n.t("label.genres"), anchor="w").grid(
            row=7, column=0, sticky="w"
        )
        self.genres_entry = ctk.CTkEntry(form, placeholder_text="fantasy, sci-fi, ...")
        self.genres_entry.grid(row=8, column=0, sticky="ew", pady=(2, 4))

        # Error label
        self.error_label = ctk.CTkLabel(form, text="", text_color="red", anchor="w")
        self.error_label.grid(row=9, column=0, sticky="w", pady=(0, 6))

        # Buttons
        btn_frame = ctk.CTkFrame(form, fg_color="transparent")
        btn_frame.grid(row=10, column=0, sticky="ew")
        btn_frame.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(
            btn_frame, text=self.i18n.t("btn.cancel"),
            fg_color="transparent", border_width=1,
            text_color=cons.BLUE_ACTIVE, border_color=cons.BLUE_ACTIVE,
            command=self.on_close
        ).grid(row=0, column=0, sticky="ew", padx=(0, 5))

        ctk.CTkButton(
            btn_frame, text=self.i18n.t("btn.save"),
            fg_color=cons.BLUE, hover_color=cons.BLUE_ACTIVE, text_color="black",
            command=self._save
        ).grid(row=0, column=1, sticky="ew", padx=(5, 0))

    def _save(self):
        title = self.title_entry.get().strip()
        if not title:
            self.error_label.configure(text=self.i18n.t("msg.field_required"))
            return

        author = self.author_entry.get().strip() or None
        publisher = self.publisher_entry.get().strip() or None
        year_str = self.year_entry.get().strip()
        year = int(year_str) if year_str else None
        count_str = self.count_entry.get().strip()
        total_count = int(count_str) if count_str else 1
        genres_raw = self.genres_entry.get().strip()
        genres = [g.strip() for g in genres_raw.split(",") if g.strip()] if genres_raw else []

        self.db.add_book(title, author, publisher, year, total_count, genres)
        self.refresh_callback()
        self.on_close()


class DeleteBook(TopLevel):
    def __init__(self, master, db, i18n, book_id, book_title, refresh_callback, parent_popup=None):
        super().__init__(master, title=i18n.t("btn.delete"), width=320, height=170, parent_popup=parent_popup)
        self.db = db
        self.i18n = i18n
        self.book_id = book_id
        self.refresh_callback = refresh_callback
        self._build(book_title)

    def _build(self, book_title: str):
        title_bar = ctk.CTkFrame(self.main_frame, fg_color="#d95050", corner_radius=0, height=40)
        title_bar.pack(fill="x")
        title_bar.pack_propagate(False)
        ctk.CTkLabel(
            title_bar, text=self.i18n.t("btn.delete"),
            font=("Arial", 14, "bold"), text_color="white",
        ).pack(side="left", padx=12, pady=8)
        ctk.CTkButton(
            title_bar, text="✕", width=32, height=28,
            fg_color="transparent", hover_color="#b03030", text_color="white",
            command=self.on_close,
        ).pack(side="right", padx=4, pady=4)

        ctk.CTkLabel(
            self.main_frame,
            text=self.i18n.t("msg.confirm_delete").format(name=book_title),
            wraplength=280, font=("Arial", 13),
        ).pack(pady=(16, 12), padx=20)

        btn_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        btn_frame.pack(pady=(0, 14))
        btn_frame.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(
            btn_frame, text=self.i18n.t("btn.cancel"),
            width=110, fg_color="transparent", border_width=1,
            text_color="#d95050", border_color="#d95050",
            command=self.on_close,
        ).grid(row=0, column=0, padx=(0, 5))

        ctk.CTkButton(
            btn_frame, text=self.i18n.t("btn.yes"),
            width=110, fg_color="#d95050", hover_color="#b03030", text_color="white",
            command=self._confirm,
        ).grid(row=0, column=1, padx=(5, 0))

    def _confirm(self):
        self.db.delete_book(self.book_id)
        self.refresh_callback()
        self._restore_parent = False
        self.on_close()


class EditBookPopup(TopLevel):
    def __init__(self, master, db, i18n, book_id, refresh_callback, parent_popup=None):
        super().__init__(master, title=i18n.t("popup.edit_book"), width=420, height=500, parent_popup=parent_popup)
        self.db = db
        self.i18n = i18n
        self.book_id = book_id
        self.refresh_callback = refresh_callback
        self._build()

    def _build(self):
        book = self.db.get_book(self.book_id)
        genres = self.db.get_book_genres(self.book_id)
        genres_str = ", ".join(g["name"] for g in genres) if genres else ""

        title_bar = ctk.CTkFrame(self.main_frame, fg_color=cons.BLUE_ACTIVE, corner_radius=0, height=40)
        title_bar.pack(fill="x")
        title_bar.pack_propagate(False)
        ctk.CTkLabel(
            title_bar, text=self.i18n.t("popup.edit_book"),
            font=("Arial", 14, "bold"), text_color="white",
        ).pack(side="left", padx=12, pady=8)
        ctk.CTkButton(
            title_bar, text="✕", width=32, height=28,
            fg_color="transparent", hover_color="#d95050", text_color="white",
            command=self.on_close,
        ).pack(side="right", padx=4, pady=4)

        form = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=24, pady=12)
        form.grid_columnconfigure(0, weight=1)

        vcmd = (self.register(lambda v: v == "" or v.isdigit()), "%P")

        ctk.CTkLabel(form, text=self.i18n.t("label.title") + " *", anchor="w").grid(
            row=0, column=0, sticky="w"
        )
        self._title_entry = ctk.CTkEntry(form)
        self._title_entry.insert(0, book["title"] or "")
        self._title_entry.grid(row=1, column=0, sticky="ew", pady=(2, 8))

        ctk.CTkLabel(form, text=self.i18n.t("label.author"), anchor="w").grid(
            row=2, column=0, sticky="w"
        )
        self._author_entry = ctk.CTkEntry(form)
        self._author_entry.insert(0, book["author_name"] or "")
        self._author_entry.grid(row=3, column=0, sticky="ew", pady=(2, 8))

        ctk.CTkLabel(form, text=self.i18n.t("label.publisher"), anchor="w").grid(
            row=4, column=0, sticky="w"
        )
        self._publisher_entry = ctk.CTkEntry(form)
        self._publisher_entry.insert(0, book["publisher"] or "")
        self._publisher_entry.grid(row=5, column=0, sticky="ew", pady=(2, 8))

        row_frame = ctk.CTkFrame(form, fg_color="transparent")
        row_frame.grid(row=6, column=0, sticky="ew", pady=(0, 8))
        row_frame.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(row_frame, text=self.i18n.t("label.year"), anchor="w").grid(
            row=0, column=0, sticky="w"
        )
        self._year_entry = ctk.CTkEntry(row_frame, validate="key", validatecommand=vcmd)
        if book["year"]:
            self._year_entry.insert(0, str(book["year"]))
        self._year_entry.grid(row=1, column=0, sticky="ew", padx=(0, 6))

        ctk.CTkLabel(row_frame, text=self.i18n.t("label.count"), anchor="w").grid(
            row=0, column=1, sticky="w"
        )
        self._count_entry = ctk.CTkEntry(row_frame, validate="key", validatecommand=vcmd)
        self._count_entry.insert(0, str(book["total_count"] or 1))
        self._count_entry.grid(row=1, column=1, sticky="ew", padx=(6, 0))

        ctk.CTkLabel(form, text=self.i18n.t("label.genres"), anchor="w").grid(
            row=7, column=0, sticky="w"
        )
        self._genres_entry = ctk.CTkEntry(form, placeholder_text="fantasy, sci-fi, ...")
        self._genres_entry.insert(0, genres_str)
        self._genres_entry.grid(row=8, column=0, sticky="ew", pady=(2, 4))

        self._error = ctk.CTkLabel(form, text="", text_color="red", anchor="w")
        self._error.grid(row=9, column=0, sticky="w", pady=(0, 6))

        btn_frame = ctk.CTkFrame(form, fg_color="transparent")
        btn_frame.grid(row=10, column=0, sticky="ew")
        btn_frame.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(
            btn_frame, text=self.i18n.t("btn.cancel"),
            fg_color="transparent", border_width=1,
            text_color=cons.BLUE_ACTIVE, border_color=cons.BLUE_ACTIVE,
            command=self.on_close,
        ).grid(row=0, column=0, sticky="ew", padx=(0, 5))

        ctk.CTkButton(
            btn_frame, text=self.i18n.t("btn.save"),
            fg_color=cons.BLUE, hover_color=cons.BLUE_ACTIVE, text_color="black",
            command=self._save,
        ).grid(row=0, column=1, sticky="ew", padx=(5, 0))

    def _save(self):
        title = self._title_entry.get().strip()
        if not title:
            self._error.configure(text=self.i18n.t("msg.field_required"))
            return

        author = self._author_entry.get().strip() or None
        publisher = self._publisher_entry.get().strip() or None
        year_s = self._year_entry.get().strip()
        year = int(year_s) if year_s else None
        count_s = self._count_entry.get().strip()
        total_count = int(count_s) if count_s else 1
        genres_raw = self._genres_entry.get().strip()
        genres = [g.strip() for g in genres_raw.split(",") if g.strip()] if genres_raw else []

        self.db.edit_book(
            self.book_id,
            title=title, author_name=author, publisher=publisher,
            year=year, total_count=total_count, genres=genres,
        )
        self.refresh_callback()
        self.on_close()


class ChangePasswordPopup(TopLevel):
    def __init__(self, master, db, i18n, admin_id: int, username: str, require_current: bool = True):
        height = 340 if require_current else 280
        super().__init__(master, title=i18n.t("popup.change_password"), width=360, height=height)
        self.db = db
        self.i18n = i18n
        self.admin_id = admin_id
        self.username = username
        self.require_current = require_current
        self._build()

    def _build(self):
        title_bar = ctk.CTkFrame(self.main_frame, fg_color=cons.BLUE_ACTIVE, corner_radius=0, height=40)
        title_bar.pack(fill="x")
        title_bar.pack_propagate(False)
        ctk.CTkLabel(
            title_bar, text=self.i18n.t("popup.change_password"),
            font=("Arial", 14, "bold"), text_color="white",
        ).pack(side="left", padx=12, pady=8)
        ctk.CTkButton(
            title_bar, text="✕", width=32, height=28,
            fg_color="transparent", hover_color="#d95050", text_color="white",
            command=self.on_close,
        ).pack(side="right", padx=4, pady=4)

        form = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=24, pady=14)
        form.grid_columnconfigure(0, weight=1)

        r = 0
        self._current_entry = None
        if self.require_current:
            ctk.CTkLabel(form, text=self.i18n.t("label.current_password") + " *", anchor="w").grid(
                row=r, column=0, sticky="w"
            )
            r += 1
            self._current_entry = ctk.CTkEntry(form, show="*")
            self._current_entry.grid(row=r, column=0, sticky="ew", pady=(2, 10))
            r += 1

        ctk.CTkLabel(form, text=self.i18n.t("label.new_password") + " *", anchor="w").grid(
            row=r, column=0, sticky="w"
        )
        r += 1
        self._new_entry = ctk.CTkEntry(form, show="*")
        self._new_entry.grid(row=r, column=0, sticky="ew", pady=(2, 10))
        r += 1

        ctk.CTkLabel(form, text=self.i18n.t("label.confirm_password") + " *", anchor="w").grid(
            row=r, column=0, sticky="w"
        )
        r += 1
        self._confirm_entry = ctk.CTkEntry(form, show="*")
        self._confirm_entry.grid(row=r, column=0, sticky="ew", pady=(2, 6))
        r += 1

        self._error = ctk.CTkLabel(form, text="", text_color="red", anchor="w")
        self._error.grid(row=r, column=0, sticky="w", pady=(0, 6))
        r += 1

        btn_frame = ctk.CTkFrame(form, fg_color="transparent")
        btn_frame.grid(row=r, column=0, sticky="ew")
        btn_frame.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(
            btn_frame, text=self.i18n.t("btn.cancel"),
            fg_color="transparent", border_width=1,
            text_color=cons.BLUE_ACTIVE, border_color=cons.BLUE_ACTIVE,
            command=self.on_close,
        ).grid(row=0, column=0, sticky="ew", padx=(0, 5))

        ctk.CTkButton(
            btn_frame, text=self.i18n.t("btn.save"),
            fg_color=cons.BLUE, hover_color=cons.BLUE_ACTIVE, text_color="black",
            command=self._save,
        ).grid(row=0, column=1, sticky="ew", padx=(5, 0))

    def _save(self):
        if self.require_current:
            current = self._current_entry.get()
            if not self.db.check_admin_password(self.username, current):
                self._error.configure(text=self.i18n.t("msg.wrong_current_password"))
                return

        new_pw = self._new_entry.get()
        confirm = self._confirm_entry.get()

        if not new_pw:
            self._error.configure(text=self.i18n.t("msg.field_required"))
            return
        if new_pw != confirm:
            self._error.configure(text=self.i18n.t("msg.passwords_mismatch"))
            return

        self.db.edit_admin(self.admin_id, password=new_pw)
        self.on_close()


class AddAdminPopup(TopLevel):
    def __init__(self, master, db, i18n, refresh_callback):
        super().__init__(master, title=i18n.t("popup.add_admin"), width=380, height=430)
        self.db = db
        self.i18n = i18n
        self.refresh_callback = refresh_callback
        self._build()

    def _build(self):
        title_bar = ctk.CTkFrame(self.main_frame, fg_color=cons.BLUE_ACTIVE, corner_radius=0, height=40)
        title_bar.pack(fill="x")
        title_bar.pack_propagate(False)
        ctk.CTkLabel(
            title_bar, text=self.i18n.t("popup.add_admin"),
            font=("Arial", 14, "bold"), text_color="white",
        ).pack(side="left", padx=12, pady=8)
        ctk.CTkButton(
            title_bar, text="✕", width=32, height=28,
            fg_color="transparent", hover_color="#d95050", text_color="white",
            command=self.on_close,
        ).pack(side="right", padx=4, pady=4)

        form = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=24, pady=14)
        form.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(form, text=self.i18n.t("label.username") + " *", anchor="w").grid(
            row=0, column=0, sticky="w"
        )
        self._username = ctk.CTkEntry(form)
        self._username.grid(row=1, column=0, sticky="ew", pady=(2, 10))

        ctk.CTkLabel(form, text=self.i18n.t("label.password") + " *", anchor="w").grid(
            row=2, column=0, sticky="w"
        )
        self._password = ctk.CTkEntry(form, show="*")
        self._password.grid(row=3, column=0, sticky="ew", pady=(2, 10))

        ctk.CTkLabel(form, text=self.i18n.t("label.confirm_password") + " *", anchor="w").grid(
            row=4, column=0, sticky="w"
        )
        self._confirm = ctk.CTkEntry(form, show="*")
        self._confirm.grid(row=5, column=0, sticky="ew", pady=(2, 10))

        ctk.CTkLabel(form, text=self.i18n.t("label.role"), anchor="w").grid(
            row=6, column=0, sticky="w"
        )
        self._role_var = ctk.StringVar(value="admin")
        ctk.CTkOptionMenu(
            form, variable=self._role_var,
            values=["admin", "superadmin"],
            fg_color=cons.CARD, button_color=cons.BLUE,
            button_hover_color=cons.BLUE_ACTIVE, text_color=cons.TEXT,
        ).grid(row=7, column=0, sticky="ew", pady=(2, 6))

        self._error = ctk.CTkLabel(form, text="", text_color="red", anchor="w")
        self._error.grid(row=8, column=0, sticky="w", pady=(0, 6))

        btn_frame = ctk.CTkFrame(form, fg_color="transparent")
        btn_frame.grid(row=9, column=0, sticky="ew")
        btn_frame.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(
            btn_frame, text=self.i18n.t("btn.cancel"),
            fg_color="transparent", border_width=1,
            text_color=cons.BLUE_ACTIVE, border_color=cons.BLUE_ACTIVE,
            command=self.on_close,
        ).grid(row=0, column=0, sticky="ew", padx=(0, 5))

        ctk.CTkButton(
            btn_frame, text=self.i18n.t("btn.save"),
            fg_color=cons.BLUE, hover_color=cons.BLUE_ACTIVE, text_color="black",
            command=self._save,
        ).grid(row=0, column=1, sticky="ew", padx=(5, 0))

    def _save(self):
        username = self._username.get().strip()
        password = self._password.get()
        confirm = self._confirm.get()

        if not username or not password:
            self._error.configure(text=self.i18n.t("msg.field_required"))
            return
        if password != confirm:
            self._error.configure(text=self.i18n.t("msg.passwords_mismatch"))
            return

        try:
            self.db.add_admin(username, password, self._role_var.get())
        except Exception:
            self._error.configure(text=self.i18n.t("msg.username_taken"))
            return

        self.refresh_callback()
        self.on_close()


class SystemLogs(TopLevel):
    def __init__(self, master):
        super().__init__(master, title="Логи системы", width=500, height=400)
