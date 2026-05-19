from .top_level import TopLevel
from .us_top_lev import UserViewPopup, ConfirmDeletePopup
from .catalog_top_lev import BookViewPopup
import customtkinter as ctk
import constantes as cons


class LeaseViewPopup(TopLevel):
    def __init__(self, master, db, i18n, lease_data, controller, refresh_callback):
        super().__init__(master, title=i18n.t("label.issue_date"), width=400, height=320)
        self.db = db
        self.i18n = i18n
        self.controller = controller
        self.refresh_callback = refresh_callback

        (self._full_name, self._title, self._issue_date,
         self._return_deadline, self._lease_id,
         self._user_id, self._book_id) = lease_data

        user_row = self.db.get_user(self._user_id)
        user = dict(user_row) if user_row else {}
        self._phone = user.get("phone") or "—"

        self._build()

    def _build(self):
        # ── Title bar ───────────────────────────────────────────────
        title_bar = ctk.CTkFrame(
            self.main_frame, fg_color=cons.BLUE_ACTIVE, corner_radius=0, height=40
        )
        title_bar.pack(fill="x")
        title_bar.pack_propagate(False)
        ctk.CTkLabel(
            title_bar, text=self._title,
            font=("Arial", 13, "bold"), text_color="white",
        ).pack(side="left", padx=12, pady=8)
        ctk.CTkButton(
            title_bar, text="✕", width=32, height=28,
            fg_color="transparent", hover_color="#d95050", text_color="white",
            command=self.on_close,
        ).pack(side="right", padx=4, pady=4)

        # ── Content ─────────────────────────────────────────────────
        body = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=20, pady=14)
        body.grid_columnconfigure(1, weight=1)

        row = 0

        # Reader
        ctk.CTkLabel(body, text=self.i18n.t("label.full_name"),
                     font=("Arial", 11), text_color="gray", anchor="w").grid(
            row=row, column=0, sticky="w", padx=(0, 12), pady=(0, 2))
        reader_text = f"{self._full_name}  {self._phone}"
        ctk.CTkButton(
            body, text=reader_text, anchor="w",
            fg_color="transparent", text_color=cons.BLUE_ACTIVE,
            hover_color=cons.GRAY,
            command=self._open_user,
        ).grid(row=row, column=1, sticky="ew", pady=(0, 2))
        row += 1

        # Book
        ctk.CTkLabel(body, text=self.i18n.t("label.title"),
                     font=("Arial", 11), text_color="gray", anchor="w").grid(
            row=row, column=0, sticky="w", padx=(0, 12), pady=(0, 2))
        ctk.CTkButton(
            body, text=self._title, anchor="w",
            fg_color="transparent", text_color=cons.BLUE_ACTIVE,
            hover_color=cons.GRAY,
            command=self._open_book,
        ).grid(row=row, column=1, sticky="ew", pady=(0, 2))
        row += 1

        # Issue date
        ctk.CTkLabel(body, text=self.i18n.t("label.issue_date"),
                     font=("Arial", 11), text_color="gray", anchor="w").grid(
            row=row, column=0, sticky="w", padx=(0, 12), pady=(0, 2))
        ctk.CTkLabel(body, text=self._issue_date or "—", anchor="w").grid(
            row=row, column=1, sticky="w", pady=(0, 2))
        row += 1

        # Return deadline
        ctk.CTkLabel(body, text=self.i18n.t("label.return_date"),
                     font=("Arial", 11), text_color="gray", anchor="w").grid(
            row=row, column=0, sticky="w", padx=(0, 12), pady=(0, 10))
        ctk.CTkLabel(body, text=self._return_deadline or "—", anchor="w").grid(
            row=row, column=1, sticky="w", pady=(0, 10))
        row += 1

        if self.controller and self.controller.is_logged_in:
            ctk.CTkButton(
                body,
                text=self.i18n.t("btn.return_book"),
                fg_color="#4CAF50", hover_color="#388E3C", text_color="white",
                command=self._confirm_return,
            ).grid(row=row, column=0, columnspan=2, sticky="ew", pady=(4, 0))

    def _open_user(self):
        win = getattr(self, "_user_win", None)
        if win is None or not win.winfo_exists():
            self._user_win = UserViewPopup(
                self.winfo_toplevel(), self.db, self.i18n, self._user_id,
                controller=self.controller,
            )
        else:
            self._user_win.focus()

    def _open_book(self):
        win = getattr(self, "_book_win", None)
        if win is None or not win.winfo_exists():
            self._book_win = BookViewPopup(
                self.winfo_toplevel(), self.db, self.i18n,
                self._book_id, self.controller,
            )
        else:
            self._book_win.focus()

    def _confirm_return(self):
        win = getattr(self, "_confirm_win", None)
        if win is None or not win.winfo_exists():
            self._confirm_win = ConfirmDeletePopup(
                self.winfo_toplevel(), self.i18n, self._title,
                self._do_return,
                msg_key="msg.confirm_return",
                title_key="btn.return_book",
                title_fg_color="#4CAF50",
            )
        else:
            self._confirm_win.focus()

    def _do_return(self):
        self.db.return_book(self._lease_id)
        self.refresh_callback()
        if self.controller:
            for cls, page in self.controller.pages.items():
                if cls.__name__ in ("CatalogPage", "MainPage"):
                    page.refresh()
        self.on_close()
