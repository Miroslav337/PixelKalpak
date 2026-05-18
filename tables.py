import customtkinter as ctk
import constantes as cons

_TAB_ICONS = ["🗒", "🕐", "≡"]
_TAB_LABELS = ["Active", "Expired", "Catalog"]


class ScrollTable(ctk.CTkFrame):
    def __init__(self, parent, columns, data_versions, table_color=cons.CARD,
                 row_factory=None, col_configs=None, tab_labels=None):
        super().__init__(parent, fg_color=table_color, corner_radius=15)

        self.columns = columns
        self.data_versions = data_versions
        self.current_version = 0
        self.rows = []
        self._tab_btns = []
        self._row_factory = row_factory
        self.col_configs = col_configs or [{"weight": 1}] * len(columns)

        self.grid_columnconfigure(0, weight=1)

        # ── tab buttons (only when multiple versions) ──────────────
        if len(data_versions) > 1:
            btn_frame = ctk.CTkFrame(self, fg_color="transparent")
            btn_frame.grid(row=0, column=0, sticky="w", padx=10, pady=(10, 4))

            for i in range(len(data_versions)):
                fallback = _TAB_LABELS[i] if i < len(_TAB_LABELS) else str(i)
                lbl = tab_labels[i] if tab_labels and i < len(tab_labels) else fallback
                label = f"{_TAB_ICONS[i]}  {lbl}"
                btn = ctk.CTkButton(
                    btn_frame,
                    text=label,
                    width=110,
                    height=32,
                    corner_radius=16,
                    font=("Arial", 13),
                    command=lambda v=i: self.load_version(v),
                    fg_color=cons.BLUE if i == 0 else "transparent",
                    text_color="black" if i == 0 else cons.BLUE_ACTIVE,
                    border_width=2,
                    border_color=cons.BLUE,
                    hover_color=cons.BLUE_ACTIVE,
                )
                btn.grid(row=0, column=i, padx=(0, 8))
                self._tab_btns.append(btn)

            search_row, scroll_row = 1, 2
        else:
            search_row, scroll_row = 0, 1

        # ── search ─────────────────────────────────────────────────
        self._search_var = ctk.StringVar()
        self._search_var.trace("w", self._on_search)

        search_frame = ctk.CTkFrame(self, fg_color=cons.BG, corner_radius=10)
        search_frame.grid(row=search_row, column=0, sticky="ew",
                          padx=10, pady=(10, 4) if search_row == 0 else (4, 6))
        search_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(search_frame, text="🔍", font=("Arial", 14)).grid(
            row=0, column=0, padx=(10, 4), pady=6
        )
        ctk.CTkEntry(
            search_frame,
            textvariable=self._search_var,
            placeholder_text="search",
            border_width=0,
            fg_color="transparent",
            font=("Arial", 13),
        ).grid(row=0, column=1, sticky="ew", padx=(0, 8), pady=4)

        # ── scrollable area ─────────────────────────────────────────
        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.grid(row=scroll_row, column=0, sticky="nsew", padx=10, pady=(0, 5))
        self.grid_rowconfigure(scroll_row, weight=1)

        if columns:
            hdr = ctk.CTkFrame(self.scroll, fg_color="transparent")
            hdr.pack(fill="x", padx=0)
            for i, cfg in enumerate(self.col_configs):
                hdr.grid_columnconfigure(i, **cfg)
            for i, col_name in enumerate(columns):
                px = (12, 0) if i == 0 else (8, 0)
                ctk.CTkLabel(
                    hdr, text=col_name,
                    font=("Arial", 13, "bold"),
                    text_color="gray",
                    anchor="w",
                ).grid(row=0, column=i, padx=px, pady=(4, 2), sticky="ew")

            ctk.CTkFrame(
                self.scroll, height=1, fg_color="gray70", corner_radius=0
            ).pack(fill="x", padx=4, pady=(0, 2))

        self.load_version(0)

    # ─────────────────────────── ROWS ──────────────────────────────

    def add_row(self, row_data):
        frame = ctk.CTkFrame(self.scroll, fg_color="transparent")
        frame.pack(fill="x", padx=0, pady=1)

        if self._row_factory:
            self._row_factory(frame, row_data, self.col_configs)
        else:
            for i, cfg in enumerate(self.col_configs):
                frame.grid_columnconfigure(i, **cfg)
            for i, value in enumerate(row_data):
                px = (12, 0) if i == 0 else (8, 0)
                ctk.CTkLabel(frame, text=str(value), anchor="w").grid(
                    row=0, column=i, sticky="ew", padx=px, pady=3
                )

        self.rows.append(frame)

    def clear(self):
        for r in self.rows:
            r.destroy()
        self.rows = []

    # ─────────────────────────── FILTER ────────────────────────────

    def _on_search(self, *_):
        self._render(self._search_var.get())

    def _render(self, query: str):
        self.clear()
        q = query.strip().lower()
        for row in self.data_versions[self.current_version]:
            if not q or any(q in str(cell).lower() for cell in row if isinstance(cell, str)):
                self.add_row(row)

    def load_version(self, version_index):
        self.current_version = version_index
        for i, btn in enumerate(self._tab_btns):
            if i == version_index:
                btn.configure(fg_color=cons.BLUE, text_color="black")
            else:
                btn.configure(fg_color="transparent", text_color=cons.BLUE_ACTIVE)
        self._render(self._search_var.get())
