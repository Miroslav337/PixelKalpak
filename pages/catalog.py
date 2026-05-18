import customtkinter as ctk
import constantes as cons
import tables
from top_labels import BookViewPopup, AddBook, ExportPopup


class CatalogPage(ctk.CTkFrame):
    def __init__(self, parent, db, i18n, controller):
        super().__init__(parent)
        self.db = db
        self.i18n = i18n
        self.controller = controller
        self.configure(fg_color=cons.BG)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._col_configs = [
            {"weight": 3},  # title
            {"weight": 2},  # author
            {"weight": 1},  # available
        ]

        self._build()
        self.refresh()

    def _build(self):
        outer = ctk.CTkFrame(self, fg_color=cons.BG)
        outer.grid(row=0, column=0, sticky="nsew", padx=20, pady=16)
        outer.grid_columnconfigure(0, weight=1)
        outer.grid_rowconfigure(1, weight=1)

        # ── action buttons ──────────────────────────────────────────
        action_row = ctk.CTkFrame(outer, fg_color="transparent")
        action_row.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        action_row.grid_columnconfigure(1, weight=1)

        self._add_book_btn = ctk.CTkButton(
            action_row,
            text=self.i18n.t("popup.add_book"),
            fg_color=cons.ACCENT,
            text_color="black",
            hover_color="#8fdb6e",
            width=140,
            command=lambda: self.open_popup(
                "add_window", AddBook, self.db, self.i18n, self._on_book_added
            ),
        )
        self._add_book_btn.grid(row=0, column=0, sticky="w")
        if not self.controller.is_logged_in:
            self._add_book_btn.grid_remove()

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
                [dict(b) for b in self.db.get_all_books()],
                "books",
            ),
        ).grid(row=0, column=2, sticky="e")

        # ── table ───────────────────────────────────────────────────
        self._table = tables.ScrollTable(
            outer,
            columns=[
                self.i18n.t("label.title"),
                self.i18n.t("label.author"),
                self.i18n.t("label.available"),
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
        # show / hide Add book button based on current login state
        if hasattr(self, "_add_book_btn"):
            if self.controller.is_logged_in:
                self._add_book_btn.grid()
            else:
                self._add_book_btn.grid_remove()

        books = [dict(r) for r in self.db.get_all_books()]
        rows = []
        for b in books:
            avail = b.get("available_count", 0) or 0
            total = b.get("total_count", 0) or 0
            avail_text = f"✓  {avail} / {total}" if avail > 0 else f"✗  0 / {total}"
            rows.append((b.get("title") or "", b.get("author_name") or "—", avail_text, b["id"]))
        self._table.data_versions[0] = rows
        self._table.load_version(0)

    def _make_row(self, frame, row_data, col_configs=None):
        title, author, avail_text, book_id = row_data
        avail_color = "#4CAF50" if avail_text.startswith("✓") else "#d95050"

        frame.configure(cursor="hand2")
        for i, cfg in enumerate(self._col_configs):
            frame.grid_columnconfigure(i, **cfg)

        title_lbl = ctk.CTkLabel(frame, text=title, anchor="w", text_color="black")
        title_lbl.grid(row=0, column=0, sticky="ew", padx=(12, 0), pady=6)

        author_lbl = ctk.CTkLabel(frame, text=author, anchor="w", text_color="gray")
        author_lbl.grid(row=0, column=1, sticky="ew", padx=(8, 0), pady=6)

        avail_lbl = ctk.CTkLabel(frame, text=avail_text, anchor="w", text_color=avail_color)
        avail_lbl.grid(row=0, column=2, sticky="ew", padx=(8, 0), pady=6)

        open_cmd = lambda bid=book_id: self.open_popup(
            "book_window", BookViewPopup,
            self.db, self.i18n, bid, self.controller, self.refresh,
        )
        for w in (frame, title_lbl, author_lbl, avail_lbl):
            w.bind("<Button-1>", lambda e, cmd=open_cmd: cmd())

    def _on_book_added(self):
        self.refresh()
        for cls, page in self.controller.pages.items():
            if cls.__name__ == "MainPage":
                page.refresh()
                break

    def open_popup(self, attr_name, popup_class, *args):
        current = getattr(self, attr_name, None)
        if current is None or not current.winfo_exists():
            setattr(self, attr_name, popup_class(self.winfo_toplevel(), *args))
        else:
            current.focus()
