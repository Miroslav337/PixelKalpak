import customtkinter as ctk
import constantes as cons
import tables
from top_labels import AddUserPopup, UserViewPopup, ExportPopup


class UsersPage(ctk.CTkFrame):
    def __init__(self, parent, db, i18n, controller):
        super().__init__(parent)
        self.db = db
        self.i18n = i18n
        self.controller = controller
        self.configure(fg_color=cons.BG)

        self._all_users = []
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._col_configs = [
            {"weight": 2},  # name
            {"weight": 2},  # phone
            {"weight": 1},  # status
        ]

        self._build()
        self.refresh()

    def _build(self):
        outer = ctk.CTkFrame(self, fg_color=cons.BG)
        outer.grid(row=0, column=0, sticky="nsew", padx=20, pady=16)
        outer.grid_columnconfigure(0, weight=1)
        outer.grid_rowconfigure(1, weight=1)

        # ── action buttons ─────────────────────────────────────────
        action_row = ctk.CTkFrame(outer, fg_color="transparent")
        action_row.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        action_row.grid_columnconfigure(1, weight=1)

        self._add_user_btn = ctk.CTkButton(
            action_row,
            text=self.i18n.t("popup.add_user"),
            fg_color=cons.ACCENT,
            text_color="black",
            hover_color="#8fdb6e",
            width=140,
            command=lambda: self.open_popup(
                "add_user_window", AddUserPopup, self.db, self.i18n, self._on_user_added
            ),
        )
        self._add_user_btn.grid(row=0, column=0, sticky="w")
        if not self.controller.is_logged_in:
            self._add_user_btn.grid_remove()

        ctk.CTkButton(
            action_row,
            text=self.i18n.t("btn.export"),
            fg_color=cons.BLUE,
            text_color="black",
            hover_color=cons.BLUE_ACTIVE,
            width=120,
            command=lambda: self.open_popup(
                "export_window", ExportPopup,
                self.i18n,
                [dict(u) for u in self.db.get_all_users()],
                "users",
            ),
        ).grid(row=0, column=2, sticky="e")

        # ── table ───────────────────────────────────────────────────
        self._table = tables.ScrollTable(
            outer,
            columns=[
                self.i18n.t("label.full_name"),
                self.i18n.t("label.phone"),
                self.i18n.t("label.status"),
            ],
            data_versions=[[]],
            table_color=cons.CARD,
            row_factory=self._make_row,
            col_configs=self._col_configs,
        )
        self._table.grid(row=1, column=0, sticky="nsew")

    def rebuild(self):
        for w in self.winfo_children():
            w.destroy()
        self._build()
        self.refresh()

    def refresh(self):
        if hasattr(self, "_add_user_btn"):
            if self.controller.is_logged_in:
                self._add_user_btn.grid()
            else:
                self._add_user_btn.grid_remove()

        self._all_users = [dict(r) for r in self.db.get_all_users()]
        rows = []
        for u in self._all_users:
            is_active = u.get("is_active", 1)
            status = self.i18n.t("label.active") if is_active else self.i18n.t("label.blocked")
            rows.append((
                u.get("full_name") or "",
                u.get("phone") or "—",
                status,
                u["id"],
            ))
        self._table.data_versions[0] = rows
        self._table.load_version(0)

    def _make_row(self, frame, row_data, col_configs=None):
        full_name, phone, status, user_id = row_data
        status_color = "#4CAF50" if status == self.i18n.t("label.active") else "#d95050"

        for i, cfg in enumerate(self._col_configs):
            frame.grid_columnconfigure(i, **cfg)

        name_lbl = ctk.CTkLabel(frame, text=full_name, anchor="w", text_color=cons.TEXT,
                                 cursor="hand2")
        name_lbl.grid(row=0, column=0, sticky="ew", padx=(12, 0), pady=6)

        phone_lbl = ctk.CTkLabel(frame, text=phone, anchor="w", text_color="gray")
        phone_lbl.grid(row=0, column=1, sticky="ew", padx=(8, 0), pady=6)

        status_lbl = ctk.CTkLabel(frame, text=status, anchor="w", text_color=status_color)
        status_lbl.grid(row=0, column=2, sticky="ew", padx=(8, 0), pady=6)

        open_cmd = lambda uid=user_id: self.open_popup(
            "view_window", UserViewPopup, self.db, self.i18n, uid, self.refresh, self.controller
        )
        for w in (frame, name_lbl, phone_lbl, status_lbl):
            w.bind("<Button-1>", lambda e, cmd=open_cmd: cmd())

    def open_popup(self, attr_name, popup_class, *args):
        current = getattr(self, attr_name, None)
        if current is None or not current.winfo_exists():
            setattr(self, attr_name, popup_class(self.winfo_toplevel(), *args))
        else:
            current.focus()

    def _on_user_added(self):
        self.refresh()
        for cls, page in self.controller.pages.items():
            if cls.__name__ == "MainPage":
                page.refresh()
                break

