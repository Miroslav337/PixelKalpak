from .top_level import TopLevel
from .admin_top_lev import EditBookPopup, DeleteBook
import customtkinter as ctk
import constantes as cons


class CatalogBookInfo(TopLevel):
    def __init__(self, master, db, i18n, book_id):
        super().__init__(master, title=i18n.t("label.title"), width=420, height=380)
        self.db = db
        self.i18n = i18n
        self.book_id = book_id
        self._build()

    def _build(self):
        book_row = self.db.get_book(self.book_id)
        book = dict(book_row) if book_row else {}
        genres = [dict(g) for g in self.db.get_book_genres(self.book_id)]

        avail = book.get("available_count", 0) or 0
        total = book.get("total_count", 0) or 0

        title_bar = ctk.CTkFrame(
            self.main_frame, fg_color=cons.BLUE_ACTIVE, corner_radius=0, height=40
        )
        title_bar.pack(fill="x")
        title_bar.pack_propagate(False)
        ctk.CTkLabel(
            title_bar, text=book.get("title", "—"),
            font=("Arial", 14, "bold"), text_color="white",
        ).pack(side="left", padx=12, pady=8)
        ctk.CTkButton(
            title_bar, text="✕", width=32, height=28,
            fg_color="transparent", hover_color="#d95050", text_color="white",
            command=self.on_close,
        ).pack(side="right", padx=4, pady=4)

        scroll = ctk.CTkScrollableFrame(self.main_frame, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        info = ctk.CTkFrame(scroll, fg_color="transparent")
        info.pack(fill="x", padx=14, pady=(12, 6))
        info.grid_columnconfigure((0, 1, 2), weight=1)

        for col, (header, value) in enumerate([
            (self.i18n.t("label.author"),    book.get("author_name") or "—"),
            (self.i18n.t("label.publisher"), book.get("publisher") or "—"),
            (self.i18n.t("label.year"),      str(book.get("year") or "—")),
        ]):
            ctk.CTkLabel(info, text=header, font=("Arial", 11),
                         text_color="gray", anchor="w").grid(
                row=0, column=col, sticky="w", padx=6, pady=(2, 0))
            ctk.CTkLabel(info, text=value, anchor="w").grid(
                row=1, column=col, sticky="w", padx=6, pady=(0, 4))

        avail_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        avail_frame.pack(fill="x", padx=14, pady=(0, 6))
        avail_frame.grid_columnconfigure((0, 1), weight=1)

        avail_color = "#4CAF50" if avail > 0 else "#d95050"
        ctk.CTkLabel(avail_frame, text=self.i18n.t("label.available"), font=("Arial", 11),
                     text_color="gray", anchor="w").grid(row=0, column=0, sticky="w", padx=6)
        ctk.CTkLabel(avail_frame, text=self.i18n.t("label.count"), font=("Arial", 11),
                     text_color="gray", anchor="w").grid(row=0, column=1, sticky="w", padx=6)
        ctk.CTkLabel(avail_frame,
                     text=f"✓  {avail}" if avail > 0 else "✗  0",
                     text_color=avail_color, anchor="w").grid(
            row=1, column=0, sticky="w", padx=6, pady=(0, 4))
        ctk.CTkLabel(avail_frame, text=str(total), anchor="w").grid(
            row=1, column=1, sticky="w", padx=6, pady=(0, 4))

        genre_names = ", ".join(g["name"] for g in genres) if genres else "—"
        genre_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        genre_frame.pack(fill="x", padx=14, pady=(0, 14))
        ctk.CTkLabel(genre_frame, text=self.i18n.t("label.genres"), font=("Arial", 11),
                     text_color="gray", anchor="w").pack(anchor="w", padx=6)
        ctk.CTkLabel(genre_frame, text=genre_names, anchor="w",
                     wraplength=370).pack(anchor="w", padx=6, pady=(2, 0))


class BookViewPopup(TopLevel):
    def __init__(self, master, db, i18n, book_id, controller, refresh_callback=None):
        super().__init__(master, title=i18n.t("label.title"), width=420, height=380)
        self.db = db
        self.i18n = i18n
        self.book_id = book_id
        self.controller = controller
        self.refresh_callback = refresh_callback
        self._build()

    def _build(self):
        for w in self.main_frame.winfo_children():
            w.destroy()

        book_row = self.db.get_book(self.book_id)
        book = dict(book_row) if book_row else {}
        genres = [dict(g) for g in self.db.get_book_genres(self.book_id)]

        avail = book.get("available_count", 0) or 0
        total = book.get("total_count", 0) or 0

        # ── Title bar ───────────────────────────────────────────────
        title_bar = ctk.CTkFrame(
            self.main_frame, fg_color=cons.BLUE_ACTIVE, corner_radius=0, height=40
        )
        title_bar.pack(fill="x")
        title_bar.pack_propagate(False)
        ctk.CTkLabel(
            title_bar, text=book.get("title", "—"),
            font=("Arial", 14, "bold"), text_color="white",
        ).pack(side="left", padx=12, pady=8)
        ctk.CTkButton(
            title_bar, text="✕", width=32, height=28,
            fg_color="transparent", hover_color="#d95050", text_color="white",
            command=self.on_close,
        ).pack(side="right", padx=4, pady=4)

        if self.controller.is_logged_in:
            ctk.CTkButton(
                title_bar, text=self.i18n.t("btn.delete"),
                height=28, fg_color="#d95050", hover_color="#b03030", text_color="white",
                command=self._open_delete,
            ).pack(side="right", padx=(0, 4), pady=4)
            ctk.CTkButton(
                title_bar, text=self.i18n.t("btn.edit"),
                height=28, fg_color=cons.ACCENT, hover_color="#8fdb6e", text_color="black",
                command=self._open_edit,
            ).pack(side="right", padx=(0, 4), pady=4)

        # ── Content ─────────────────────────────────────────────────
        scroll = ctk.CTkScrollableFrame(self.main_frame, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        info = ctk.CTkFrame(scroll, fg_color="transparent")
        info.pack(fill="x", padx=14, pady=(12, 6))
        info.grid_columnconfigure((0, 1, 2), weight=1)

        for col, (header, value) in enumerate([
            (self.i18n.t("label.author"),    book.get("author_name") or "—"),
            (self.i18n.t("label.publisher"), book.get("publisher") or "—"),
            (self.i18n.t("label.year"),      str(book.get("year") or "—")),
        ]):
            ctk.CTkLabel(info, text=header, font=("Arial", 11),
                         text_color="gray", anchor="w").grid(
                row=0, column=col, sticky="w", padx=6, pady=(2, 0))
            ctk.CTkLabel(info, text=value, anchor="w").grid(
                row=1, column=col, sticky="w", padx=6, pady=(0, 4))

        avail_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        avail_frame.pack(fill="x", padx=14, pady=(0, 6))
        avail_frame.grid_columnconfigure((0, 1), weight=1)

        avail_color = "#4CAF50" if avail > 0 else "#d95050"
        ctk.CTkLabel(avail_frame, text=self.i18n.t("label.available"), font=("Arial", 11),
                     text_color="gray", anchor="w").grid(row=0, column=0, sticky="w", padx=6)
        ctk.CTkLabel(avail_frame, text=self.i18n.t("label.count"), font=("Arial", 11),
                     text_color="gray", anchor="w").grid(row=0, column=1, sticky="w", padx=6)
        ctk.CTkLabel(avail_frame,
                     text=f"✓  {avail}" if avail > 0 else "✗  0",
                     text_color=avail_color, anchor="w").grid(
            row=1, column=0, sticky="w", padx=6, pady=(0, 4))
        ctk.CTkLabel(avail_frame, text=str(total), anchor="w").grid(
            row=1, column=1, sticky="w", padx=6, pady=(0, 4))

        genre_names = ", ".join(g["name"] for g in genres) if genres else "—"
        genre_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        genre_frame.pack(fill="x", padx=14, pady=(0, 14))
        ctk.CTkLabel(genre_frame, text=self.i18n.t("label.genres"), font=("Arial", 11),
                     text_color="gray", anchor="w").pack(anchor="w", padx=6)
        ctk.CTkLabel(genre_frame, text=genre_names, anchor="w",
                     wraplength=370).pack(anchor="w", padx=6, pady=(2, 0))

    def _reload(self):
        if self.refresh_callback:
            self.refresh_callback()
        self._build()

    def _refresh_all(self):
        if self.refresh_callback:
            self.refresh_callback()
        if self.controller:
            for cls, page in self.controller.pages.items():
                if cls.__name__ == "MainPage":
                    page.refresh()
                    break

    def _open_edit(self):
        win = getattr(self, "_edit_win", None)
        if win is None or not win.winfo_exists():
            self._edit_win = EditBookPopup(
                self.winfo_toplevel(), self.db, self.i18n,
                self.book_id, self._reload,
                parent_popup=self,
            )
        else:
            self._edit_win.focus()

    def _open_delete(self):
        book_row = self.db.get_book(self.book_id)
        book_title = dict(book_row).get("title", "?") if book_row else "?"
        win = getattr(self, "_delete_win", None)
        if win is None or not win.winfo_exists():
            self._delete_win = DeleteBook(
                self.winfo_toplevel(), self.db, self.i18n,
                self.book_id, book_title, self._refresh_all,
                parent_popup=self,
            )
        else:
            self._delete_win.focus()
