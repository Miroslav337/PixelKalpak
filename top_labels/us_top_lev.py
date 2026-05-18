from .top_level import TopLevel
import customtkinter as ctk
import constantes as cons
from datetime import date, timedelta


class AddUserPopup(TopLevel):
    def __init__(self, master, db, i18n, refresh_callback):
        super().__init__(master, title=i18n.t("popup.add_user"), width=380, height=380)
        self.db = db
        self.i18n = i18n
        self.refresh_callback = refresh_callback
        self._build()

    def _build(self):
        # Title bar
        title_bar = ctk.CTkFrame(
            self.main_frame, fg_color=cons.ACCENT, corner_radius=0, height=40
        )
        title_bar.pack(fill="x")
        title_bar.pack_propagate(False)
        ctk.CTkLabel(
            title_bar, text=self.i18n.t("popup.add_user"),
            font=("Arial", 14, "bold"), text_color="black",
        ).pack(side="left", padx=12, pady=8)
        ctk.CTkButton(
            title_bar, text="✕", width=32, height=28,
            fg_color="transparent", hover_color="#d95050", text_color="black",
            command=self.on_close,
        ).pack(side="right", padx=4, pady=4)

        form = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=24, pady=14)
        form.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(form, text=self.i18n.t("label.full_name") + " *", anchor="w").grid(
            row=0, column=0, sticky="w"
        )
        self.name_entry = ctk.CTkEntry(form)
        self.name_entry.grid(row=1, column=0, sticky="ew", pady=(2, 10))

        ctk.CTkLabel(form, text=self.i18n.t("label.phone"), anchor="w").grid(
            row=2, column=0, sticky="w"
        )
        self.phone_entry = ctk.CTkEntry(form)
        self.phone_entry.grid(row=3, column=0, sticky="ew", pady=(2, 10))

        ctk.CTkLabel(form, text=self.i18n.t("label.gender"), anchor="w").grid(
            row=4, column=0, sticky="w"
        )
        self._gender_labels = [
            self.i18n.t("gender.unspecified"),
            self.i18n.t("gender.m"),
            self.i18n.t("gender.f"),
        ]
        self.gender_var = ctk.StringVar(value=self._gender_labels[0])
        ctk.CTkOptionMenu(
            form,
            variable=self.gender_var,
            values=self._gender_labels,
            fg_color=cons.CARD,
            button_color=cons.BLUE,
            button_hover_color=cons.BLUE_ACTIVE,
            text_color="black",
        ).grid(row=5, column=0, sticky="ew", pady=(2, 6))

        self.error_label = ctk.CTkLabel(form, text="", text_color="red", anchor="w")
        self.error_label.grid(row=6, column=0, sticky="w", pady=(0, 6))

        btn_frame = ctk.CTkFrame(form, fg_color="transparent")
        btn_frame.grid(row=7, column=0, sticky="ew")
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
        full_name = self.name_entry.get().strip()
        if not full_name:
            self.error_label.configure(text=self.i18n.t("msg.field_required"))
            return
        phone = self.phone_entry.get().strip() or None
        gender_val = self.gender_var.get()
        _gender_db = {
            self._gender_labels[0]: None,
            self._gender_labels[1]: "М",
            self._gender_labels[2]: "Ж",
        }
        gender = _gender_db.get(gender_val)
        self.db.add_user(full_name, phone, gender)
        self.refresh_callback()
        self.on_close()


class UserViewPopup(TopLevel):
    def __init__(self, master, db, i18n, user_id, refresh_callback=None, controller=None):
        super().__init__(master, title=i18n.t("popup.user_info"), width=420, height=560)
        self.db = db
        self.i18n = i18n
        self.user_id = user_id
        self.refresh_callback = refresh_callback
        self.controller = controller
        self._build()

    def _build(self):
        user_row = self.db.get_user(self.user_id)
        user = dict(user_row) if user_row else {}
        history = [dict(h) for h in self.db.get_user_history(self.user_id)]
        active = [h for h in history if h["status"] == "на руках"]

        # Title bar (shows user name)
        title_bar = ctk.CTkFrame(
            self.main_frame, fg_color=cons.BLUE, corner_radius=0, height=40
        )
        title_bar.pack(fill="x")
        title_bar.pack_propagate(False)
        ctk.CTkLabel(
            title_bar, text=user.get("full_name", "—"),
            font=("Arial", 14, "bold"), text_color="black",
        ).pack(side="left", padx=12, pady=8)
        ctk.CTkButton(
            title_bar, text="✕", width=32, height=28,
            fg_color="transparent", hover_color="#d95050", text_color="black",
            command=self.on_close,
        ).pack(side="right", padx=4, pady=4)

        is_admin = self.controller and self.controller.is_logged_in
        if is_admin:
            ctk.CTkButton(
                title_bar, text=self.i18n.t("btn.issue"), height=28,
                fg_color=cons.ACCENT, hover_color="#8fdb6e", text_color="black",
                command=self._open_issue,
            ).pack(side="right", padx=(0, 4), pady=4)

        # Scrollable content
        scroll = ctk.CTkScrollableFrame(self.main_frame, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        # ── Section 1: main info ──────────────────────────────────
        self._section_header(scroll, self.i18n.t("popup.user_info"))

        info = ctk.CTkFrame(scroll, fg_color="transparent")
        info.pack(fill="x", padx=14, pady=(4, 8))
        info.grid_columnconfigure((0, 1, 2), weight=1)

        cols = [
            (self.i18n.t("label.full_name"),  user.get("full_name") or "—"),
            (self.i18n.t("label.reg_date"),    user.get("registration_date") or "—"),
            (self.i18n.t("label.phone"),       user.get("phone") or "—"),
        ]
        for col, (header, value) in enumerate(cols):
            ctk.CTkLabel(info, text=header, font=("Arial", 11),
                         text_color="gray", anchor="w").grid(
                row=0, column=col, sticky="w", padx=6, pady=(2, 0)
            )
            ctk.CTkLabel(info, text=value, anchor="w").grid(
                row=1, column=col, sticky="w", padx=6, pady=(0, 4)
            )

        # ── Section 2: notes ─────────────────────────────────────
        self._section_header(scroll, self.i18n.t("label.notes"))

        notes_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        notes_frame.pack(fill="x", padx=14, pady=(4, 8))
        notes_frame.grid_columnconfigure(0, weight=1)

        notes_box = ctk.CTkTextbox(notes_frame, height=70, state="normal")
        notes_box.grid(row=0, column=0, columnspan=2, sticky="ew")
        notes_val = user.get("notes") or ""
        if notes_val:
            notes_box.insert("1.0", notes_val)
        notes_box.configure(state="disabled")

        if is_admin:
            ctk.CTkButton(
                notes_frame, text=self.i18n.t("btn.edit"), width=70,
                fg_color="transparent", border_width=1,
                border_color=cons.BLUE, text_color=cons.BLUE_ACTIVE,
                command=self._open_edit,
            ).grid(row=1, column=1, sticky="e", pady=(4, 0))

        # ── Section 3: active readings ────────────────────────────
        self._section_header(scroll, self.i18n.t("label.status"))

        status_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        status_frame.pack(fill="x", padx=14, pady=(4, 8))
        status_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(status_frame, text=self.i18n.t("label.status"), font=("Arial", 11),
                     text_color="gray", anchor="w").grid(
            row=0, column=0, sticky="w", padx=(6, 20), pady=(2, 0)
        )
        ctk.CTkLabel(status_frame, text=self.i18n.t("label.title"), font=("Arial", 11),
                     text_color="gray", anchor="w").grid(
            row=0, column=1, sticky="w", padx=6, pady=(2, 0)
        )

        if active:
            for i, h in enumerate(active, start=1):
                ctk.CTkLabel(status_frame, text=self.i18n.t("label.active"),
                             text_color="#4CAF50", anchor="w").grid(
                    row=i, column=0, sticky="w", padx=(6, 20), pady=2
                )
                ctk.CTkLabel(status_frame, text=h["title"], anchor="w").grid(
                    row=i, column=1, sticky="w", padx=6, pady=2
                )
        else:
            ctk.CTkLabel(status_frame, text="—", text_color="gray").grid(
                row=1, column=0, columnspan=2, sticky="w", padx=6, pady=4
            )

        # ── Section 4: history ────────────────────────────────────
        self._section_header(scroll, self.i18n.t("popup.history"))

        hist_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        hist_frame.pack(fill="x", padx=14, pady=(4, 14))
        hist_frame.grid_columnconfigure(0, weight=2)
        hist_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(hist_frame, text=self.i18n.t("label.title"), font=("Arial", 11),
                     text_color="gray", anchor="w").grid(
            row=0, column=0, sticky="w", padx=6, pady=(2, 0)
        )
        ctk.CTkLabel(hist_frame, text=self.i18n.t("label.issue_date"), font=("Arial", 11),
                     text_color="gray", anchor="w").grid(
            row=0, column=1, sticky="w", padx=6, pady=(2, 0)
        )

        if history:
            for i, h in enumerate(history, start=1):
                ctk.CTkLabel(hist_frame, text=h["title"], anchor="w").grid(
                    row=i, column=0, sticky="w", padx=6, pady=2
                )
                ctk.CTkLabel(hist_frame, text=h["issue_date"] or "—", anchor="w").grid(
                    row=i, column=1, sticky="w", padx=6, pady=2
                )
        else:
            ctk.CTkLabel(hist_frame, text="—", text_color="gray").grid(
                row=1, column=0, columnspan=2, sticky="w", padx=6, pady=4
            )

    def _open_edit(self):
        win = getattr(self, "_edit_win", None)
        if win is None or not win.winfo_exists():
            self._edit_win = UserEditPopup(
                self.winfo_toplevel(), self.db, self.i18n,
                self.user_id, self._on_edit_saved,
                parent_popup=self,
                controller=self.controller,
            )
        else:
            self._edit_win.focus()

    def _on_edit_saved(self):
        if self.refresh_callback:
            self.refresh_callback()
        for w in self.main_frame.winfo_children():
            w.destroy()
        self._build()

    def _open_issue(self):
        win = getattr(self, "_issue_win", None)
        if win is None or not win.winfo_exists():
            loan_days = self.controller.settings.loan_days if self.controller else 30
            self._issue_win = IssueBookPopup(
                self.winfo_toplevel(), self.db, self.i18n,
                self.user_id, self._on_issue_saved,
                loan_days=loan_days,
                parent_popup=self,
            )
        else:
            self._issue_win.focus()

    def _on_issue_saved(self):
        if self.refresh_callback:
            self.refresh_callback()
        if self.controller:
            for cls, page in self.controller.pages.items():
                if cls.__name__ in ("MainPage", "CatalogPage"):
                    page.refresh()
        for w in self.main_frame.winfo_children():
            w.destroy()
        self._build()

    def _section_header(self, parent, title: str):
        header = ctk.CTkFrame(parent, fg_color=cons.ACCENT, corner_radius=6, height=28)
        header.pack(fill="x", padx=12, pady=(8, 2))
        header.pack_propagate(False)
        ctk.CTkLabel(
            header, text=title, font=("Arial", 12, "bold"), text_color="black"
        ).pack(side="left", padx=10)


class UserEditPopup(TopLevel):
    def __init__(self, master, db, i18n, user_id, refresh_callback, parent_popup=None, controller=None):
        super().__init__(master, title=i18n.t("popup.edit_user"), width=380, height=560, parent_popup=parent_popup)
        self.db = db
        self.i18n = i18n
        self.user_id = user_id
        self.refresh_callback = refresh_callback
        self.controller = controller
        self._build()

    def _build(self):
        user_row = self.db.get_user(self.user_id)
        user = dict(user_row) if user_row else {}

        title_bar = ctk.CTkFrame(
            self.main_frame, fg_color=cons.BLUE, corner_radius=0, height=40
        )
        title_bar.pack(fill="x")
        title_bar.pack_propagate(False)
        ctk.CTkLabel(
            title_bar, text=self.i18n.t("popup.edit_user"),
            font=("Arial", 14, "bold"), text_color="black",
        ).pack(side="left", padx=12, pady=8)
        ctk.CTkButton(
            title_bar, text="✕", width=32, height=28,
            fg_color="transparent", hover_color="#d95050", text_color="black",
            command=self.on_close,
        ).pack(side="right", padx=4, pady=4)

        form = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=14, pady=10)
        form.grid_columnconfigure(0, weight=1)

        r = 0
        self._grid_section_header(form, self.i18n.t("section.data"), r); r += 1

        ctk.CTkLabel(form, text=self.i18n.t("label.full_name") + " *", anchor="w").grid(
            row=r, column=0, sticky="w", padx=6, pady=(8, 0)); r += 1
        self.name_entry = ctk.CTkEntry(form)
        self.name_entry.grid(row=r, column=0, sticky="ew", padx=6, pady=(2, 6))
        self.name_entry.insert(0, user.get("full_name") or ""); r += 1

        ctk.CTkLabel(form, text=self.i18n.t("label.phone"), anchor="w").grid(
            row=r, column=0, sticky="w", padx=6); r += 1
        self.phone_entry = ctk.CTkEntry(form)
        self.phone_entry.grid(row=r, column=0, sticky="ew", padx=6, pady=(2, 6))
        self.phone_entry.insert(0, user.get("phone") or ""); r += 1

        ctk.CTkLabel(form, text=self.i18n.t("label.gender"), anchor="w").grid(
            row=r, column=0, sticky="w", padx=6); r += 1
        self._gender_labels = [
            self.i18n.t("gender.unspecified"),
            self.i18n.t("gender.m"),
            self.i18n.t("gender.f"),
        ]
        _db_to_label = {"М": self._gender_labels[1], "Ж": self._gender_labels[2]}
        gender_display = _db_to_label.get(user.get("gender") or "", self._gender_labels[0])
        self.gender_var = ctk.StringVar(value=gender_display)
        ctk.CTkOptionMenu(
            form,
            variable=self.gender_var,
            values=self._gender_labels,
            fg_color=cons.CARD,
            button_color=cons.BLUE,
            button_hover_color=cons.BLUE_ACTIVE,
            text_color="black",
        ).grid(row=r, column=0, sticky="ew", padx=6, pady=(2, 10)); r += 1

        self._grid_section_header(form, self.i18n.t("label.notes"), r); r += 1

        self.notes_box = ctk.CTkTextbox(form, height=80)
        self.notes_box.grid(row=r, column=0, sticky="ew", padx=6, pady=(8, 6))
        notes_val = user.get("notes") or ""
        if notes_val:
            self.notes_box.insert("1.0", notes_val)
        r += 1

        self.error_label = ctk.CTkLabel(form, text="", text_color="red", anchor="w")
        self.error_label.grid(row=r, column=0, sticky="w", padx=6, pady=(0, 4)); r += 1

        btn_frame = ctk.CTkFrame(form, fg_color="transparent")
        btn_frame.grid(row=r, column=0, sticky="ew", padx=6)
        btn_frame.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(
            btn_frame, text=self.i18n.t("btn.cancel"),
            fg_color="transparent", border_width=1,
            text_color=cons.BLUE_ACTIVE, border_color=cons.BLUE_ACTIVE,
            command=self.on_close,
        ).grid(row=0, column=0, sticky="ew", padx=(0, 5))

        ctk.CTkButton(
            btn_frame, text=self.i18n.t("btn.save_all"),
            fg_color=cons.BLUE, hover_color=cons.BLUE_ACTIVE, text_color="black",
            command=self._save,
        ).grid(row=0, column=1, sticky="ew", padx=(5, 0))

        ctk.CTkButton(
            btn_frame, text=self.i18n.t("btn.delete"),
            fg_color="#d95050", hover_color="#b03030", text_color="white",
            command=self._open_delete,
        ).grid(row=1, column=0, columnspan=2, sticky="ew", pady=(8, 0))

    def _grid_section_header(self, parent, title: str, row: int):
        header = ctk.CTkFrame(parent, fg_color=cons.ACCENT, corner_radius=6, height=28)
        header.grid(row=row, column=0, sticky="ew", padx=4, pady=(4, 2))
        header.grid_propagate(False)
        ctk.CTkLabel(
            header, text=title, font=("Arial", 12, "bold"), text_color="black"
        ).pack(side="left", padx=10)

    def _save(self):
        full_name = self.name_entry.get().strip()
        if not full_name:
            self.error_label.configure(text=self.i18n.t("msg.field_required"))
            return
        phone = self.phone_entry.get().strip() or None
        _label_to_db = {
            self._gender_labels[0]: None,
            self._gender_labels[1]: "М",
            self._gender_labels[2]: "Ж",
        }
        gender = _label_to_db.get(self.gender_var.get())
        notes = self.notes_box.get("1.0", "end").strip() or None

        self.db.edit_user(self.user_id, full_name=full_name, phone=phone, gender=gender)
        self.db.edit_user_notes(self.user_id, notes)
        self.refresh_callback()
        self.on_close()

    def _open_delete(self):
        user_row = self.db.get_user(self.user_id)
        user = dict(user_row) if user_row else {}
        name = user.get("full_name", "?")
        win = getattr(self, "_delete_win", None)
        if win is None or not win.winfo_exists():
            self._delete_win = ConfirmDeletePopup(
                self.winfo_toplevel(), self.i18n, name,
                self._do_delete,
                parent_popup=self,
            )
        else:
            self._delete_win.focus()

    def _do_delete(self):
        self.db.delete_user(self.user_id)
        if self.controller:
            for cls, page in self.controller.pages.items():
                if cls.__name__ in ("UsersPage", "MainPage"):
                    page.refresh()
        elif self.refresh_callback:
            self.refresh_callback()
        if hasattr(self, "_delete_win") and self._delete_win.winfo_exists():
            self._delete_win._restore_parent = False


class ConfirmDeletePopup(TopLevel):
    def __init__(self, master, i18n, name: str, on_confirm,
                 msg_key="msg.confirm_delete", parent_popup=None,
                 title_key="btn.delete", title_fg_color="#d95050"):
        super().__init__(master, title=i18n.t(title_key), width=320, height=170, parent_popup=parent_popup)
        self.i18n = i18n
        self._on_confirm = on_confirm
        self._msg_key = msg_key
        self._title_key = title_key
        self._title_fg_color = title_fg_color
        self._build(name)

    def _build(self, name: str):
        is_delete = self._title_fg_color == "#d95050"
        text_color = "white" if is_delete else "black"
        hover_color = "#c03030" if is_delete else "#388E3C"

        title_bar = ctk.CTkFrame(
            self.main_frame, fg_color=self._title_fg_color, corner_radius=0, height=40
        )
        title_bar.pack(fill="x")
        title_bar.pack_propagate(False)
        ctk.CTkLabel(
            title_bar, text=self.i18n.t(self._title_key),
            font=("Arial", 14, "bold"), text_color=text_color,
        ).pack(side="left", padx=12, pady=8)
        ctk.CTkButton(
            title_bar, text="✕", width=32, height=28,
            fg_color="transparent", hover_color=hover_color, text_color=text_color,
            command=self.on_close,
        ).pack(side="right", padx=4, pady=4)

        ctk.CTkLabel(
            self.main_frame,
            text=self.i18n.t(self._msg_key).format(name=name),
            font=("Arial", 14),
        ).pack(pady=(20, 16))

        btn_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20)
        btn_frame.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(
            btn_frame, text=self.i18n.t("btn.cancel"),
            fg_color="transparent", border_width=1,
            text_color="gray", border_color="gray",
            command=self.on_close,
        ).grid(row=0, column=0, sticky="ew", padx=(0, 5))

        confirm_fg = self._title_fg_color
        ctk.CTkButton(
            btn_frame, text=self.i18n.t("btn.yes"),
            fg_color=confirm_fg, hover_color=hover_color, text_color=text_color,
            command=self._confirm,
        ).grid(row=0, column=1, sticky="ew", padx=(5, 0))

    def _confirm(self):
        self._on_confirm()
        self.on_close()


class IssueBookPopup(TopLevel):
    def __init__(self, master, db, i18n, user_id, refresh_callback, loan_days=30, parent_popup=None):
        super().__init__(master, title=i18n.t("btn.issue"), width=420, height=500, parent_popup=parent_popup)
        self.db = db
        self.i18n = i18n
        self.user_id = user_id
        self.refresh_callback = refresh_callback
        self._loan_days = loan_days
        self._book_map = {}          # label → book_id
        self._btn_map = {}           # label → CTkButton
        self._selected_book_id = None
        self._selected_label = None
        self._build()

    def _build(self):
        user_row = self.db.get_user(self.user_id)
        user = dict(user_row) if user_row else {}
        user_name = user.get("full_name") or "—"

        all_books = [dict(b) for b in self.db.get_all_books()]
        available = [b for b in all_books if (b.get("available_count") or 0) > 0]
        for b in available:
            lbl = f"{b['title']} — {b.get('author_name') or '—'}  ({b['available_count']})"
            self._book_map[lbl] = b["id"]

        # ── Title bar ───────────────────────────────────────────────
        title_bar = ctk.CTkFrame(
            self.main_frame, fg_color=cons.BLUE, corner_radius=0, height=40
        )
        title_bar.pack(fill="x")
        title_bar.pack_propagate(False)
        ctk.CTkLabel(
            title_bar,
            text=f"{self.i18n.t('btn.issue')} — {user_name}",
            font=("Arial", 13, "bold"), text_color="black",
        ).pack(side="left", padx=12, pady=8)
        ctk.CTkButton(
            title_bar, text="✕", width=32, height=28,
            fg_color="transparent", hover_color="#d95050", text_color="black",
            command=self.on_close,
        ).pack(side="right", padx=4, pady=4)

        # ── Buttons + error — pinned to bottom before form ─────────────
        btn_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        btn_frame.pack(side="bottom", fill="x", padx=24, pady=(0, 16))
        btn_frame.grid_columnconfigure((0, 1), weight=1)

        self._error_label = ctk.CTkLabel(
            btn_frame, text="", text_color="red", anchor="w"
        )
        self._error_label.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 4))

        ctk.CTkButton(
            btn_frame, text=self.i18n.t("btn.cancel"),
            fg_color="transparent", border_width=1,
            text_color=cons.BLUE_ACTIVE, border_color=cons.BLUE_ACTIVE,
            command=self.on_close,
        ).grid(row=1, column=0, sticky="ew", padx=(0, 5))

        self._issue_btn = ctk.CTkButton(
            btn_frame, text=self.i18n.t("btn.issue"),
            fg_color=cons.ACCENT, hover_color="#8fdb6e", text_color="black",
            command=self._issue,
            state="disabled" if not self._book_map else "normal",
        )
        self._issue_btn.grid(row=1, column=1, sticky="ew", padx=(5, 0))

        # ── Form content ────────────────────────────────────────────
        form = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=24, pady=(16, 8))
        form.grid_columnconfigure(0, weight=1)

        r = 0
        ctk.CTkLabel(form, text=self.i18n.t("label.select_book"), anchor="w").grid(
            row=r, column=0, sticky="w"); r += 1

        if not self._book_map:
            ctk.CTkLabel(
                form, text=self.i18n.t("msg.no_books_available"),
                text_color="#d95050", anchor="w",
            ).grid(row=r, column=0, sticky="w", pady=(4, 10)); r += 1
        else:
            self._book_search_var = ctk.StringVar()
            self._book_search_var.trace("w", self._on_book_search)
            ctk.CTkEntry(
                form, textvariable=self._book_search_var,
                placeholder_text="🔍",
            ).grid(row=r, column=0, sticky="ew", pady=(4, 4)); r += 1

            self._book_list_frame = ctk.CTkScrollableFrame(form, height=140, fg_color=cons.CARD)
            self._book_list_frame.grid(row=r, column=0, sticky="ew", pady=(0, 10))
            self._book_list_frame.grid_columnconfigure(0, weight=1)
            self._build_book_list("")
            r += 1

        ctk.CTkLabel(
            form,
            text=self.i18n.t("label.return_deadline"),
            anchor="w",
        ).grid(row=r, column=0, sticky="w"); r += 1

        _default = date.today() + timedelta(days=self._loan_days)
        date_row = ctk.CTkFrame(form, fg_color="transparent")
        date_row.grid(row=r, column=0, sticky="ew", pady=(2, 10)); r += 1
        date_row.grid_columnconfigure(0, weight=1)
        date_row.grid_columnconfigure(1, weight=1)
        date_row.grid_columnconfigure(2, weight=2)

        self._day_var   = ctk.StringVar(value=f"{_default.day:02d}")
        self._month_var = ctk.StringVar(value=f"{_default.month:02d}")
        self._year_var  = ctk.StringVar(value=str(_default.year))

        ctk.CTkOptionMenu(
            date_row, variable=self._day_var,
            values=[f"{d:02d}" for d in range(1, 32)],
            fg_color=cons.CARD, button_color=cons.BLUE,
            button_hover_color=cons.BLUE_ACTIVE, text_color="black",
        ).grid(row=0, column=0, sticky="ew", padx=(0, 4))
        ctk.CTkOptionMenu(
            date_row, variable=self._month_var,
            values=[f"{m:02d}" for m in range(1, 13)],
            fg_color=cons.CARD, button_color=cons.BLUE,
            button_hover_color=cons.BLUE_ACTIVE, text_color="black",
        ).grid(row=0, column=1, sticky="ew", padx=4)
        ctk.CTkOptionMenu(
            date_row, variable=self._year_var,
            values=[str(date.today().year + i) for i in range(4)],
            fg_color=cons.CARD, button_color=cons.BLUE,
            button_hover_color=cons.BLUE_ACTIVE, text_color="black",
        ).grid(row=0, column=2, sticky="ew", padx=(4, 0))


    def _build_book_list(self, query: str):
        for w in self._book_list_frame.winfo_children():
            w.destroy()
        self._btn_map = {}
        q = query.strip().lower()
        for row_idx, (lbl, book_id) in enumerate(self._book_map.items()):
            if q and q not in lbl.lower():
                continue
            btn = ctk.CTkButton(
                self._book_list_frame,
                text=lbl,
                anchor="w",
                fg_color=cons.BLUE if lbl == self._selected_label else "transparent",
                text_color="black",
                hover_color=cons.BLUE_ACTIVE,
                command=lambda l=lbl, bid=book_id: self._select_book(l, bid),
            )
            btn.grid(row=row_idx, column=0, sticky="ew", padx=4, pady=2)
            self._btn_map[lbl] = btn

    def _on_book_search(self, *_):
        self._build_book_list(self._book_search_var.get())

    def _select_book(self, label: str, book_id: int):
        prev = self._selected_label
        self._selected_label = label
        self._selected_book_id = book_id
        if prev and prev in self._btn_map:
            self._btn_map[prev].configure(fg_color="transparent")
        if label in self._btn_map:
            self._btn_map[label].configure(fg_color=cons.BLUE)

    def _issue(self):
        if not self._selected_book_id:
            self._error_label.configure(text=self.i18n.t("msg.field_required"))
            return

        try:
            deadline = date(
                int(self._year_var.get()),
                int(self._month_var.get()),
                int(self._day_var.get()),
            )
        except ValueError:
            self._error_label.configure(text=self.i18n.t("msg.invalid_date"))
            return

        if deadline < date.today():
            self._error_label.configure(text=self.i18n.t("msg.date_in_past"))
            return

        try:
            self.db.issue_book(self.user_id, self._selected_book_id, str(deadline))
        except Exception as e:
            self._error_label.configure(text=str(e))
            return

        cb = self.refresh_callback
        self.after_idle(lambda c=cb: (self.on_close(), c()))
