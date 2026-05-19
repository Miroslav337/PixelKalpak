import os
import customtkinter as ctk
from PIL import Image
import constantes as cons
import tables
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
import matplotlib.pyplot as _plt
from top_labels import LeaseViewPopup

_IMG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "image")


class MainPage(ctk.CTkFrame):
    def __init__(self, parent, db, i18n, controller):
        super().__init__(parent)
        self.db = db
        self.i18n = i18n
        self.controller = controller
        self.configure(fg_color=cons.BG)
        self._icons = []

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build()

    # ─────────────────────────── BUILD ─────────────────────────────

    def _build(self):
        container = ctk.CTkFrame(self, fg_color=cons.BG)
        container.grid(row=0, column=0, sticky="nsew", padx=20, pady=16)

        # narrow left (cards) + two wider columns (charts)
        container.grid_columnconfigure(0, weight=1)
        container.grid_columnconfigure((1, 2), weight=2)
        container.grid_rowconfigure(2, weight=1)

        # ── stat cards (stacked in col 0) ───────────────────────────
        self._card(
            container,
            title=self.i18n.t("stats.on_hands"),
            value=str(self._stat_on_hands()),
            row=0, col=0,
            icon_path=os.path.join(_IMG_DIR, "on_hand.png"),
        )
        self._card(
            container,
            title=self.i18n.t("stats.readers"),
            value=str(self._stat_total_users()),
            row=1, col=0,
            icon_path=os.path.join(_IMG_DIR, "reader.png"),
        )

        # ── charts (span both card rows, cols 1 and 2) ──────────────
        self._chart_genres(container,  self._stat_top_genres(),    row=0, col=1, rowspan=2)
        self._chart_monthly(container, self._stat_monthly_issues(), row=0, col=2, rowspan=2)

        # ── table ───────────────────────────────────────────────────
        self._lease_col_configs = [
            {"weight": 2},
            {"weight": 2},
            {"weight": 1},
            {"weight": 1},
        ]
        columns = [
            self.i18n.t("label.full_name"),
            self.i18n.t("label.title"),
            self.i18n.t("label.issue_date"),
            self.i18n.t("label.return_date"),
        ]
        active  = self._lease_rows(self.db.get_active_leases())
        overdue = self._lease_rows(self.db.get_overdue_leases())

        self._tbl = tables.ScrollTable(
            container, columns, [active, overdue],
            table_color=cons.CARD,
            row_factory=self._make_lease_row,
            col_configs=self._lease_col_configs,
            tab_labels=[self.i18n.t("table.active"), self.i18n.t("table.expired")],
        )
        self._tbl.grid(row=2, column=0, columnspan=3, sticky="nsew", padx=10, pady=10)

    # ─────────────────────────── QUERIES ───────────────────────────

    def _stat_on_hands(self) -> int:
        row = self.db.conn.execute(
            "SELECT COUNT(*) FROM Lease_History WHERE status = 'на руках'"
        ).fetchone()
        return row[0] if row else 0

    def _stat_total_users(self) -> int:
        row = self.db.conn.execute("SELECT COUNT(*) FROM Users").fetchone()
        return row[0] if row else 0

    def _stat_monthly_issues(self) -> list:
        rows = self.db.conn.execute(
            """SELECT strftime('%Y-%m', issue_date) AS month, COUNT(*) AS cnt
               FROM Lease_History
               GROUP BY month ORDER BY month DESC LIMIT 6"""
        ).fetchall()
        return [(r[0], r[1]) for r in reversed(rows)]

    def _stat_top_genres(self) -> list:
        rows = self.db.conn.execute(
            """SELECT Genres.name, COUNT(*) AS cnt
               FROM Lease_History
               JOIN Book_Genres ON Lease_History.book_id = Book_Genres.book_id
               JOIN Genres      ON Book_Genres.genre_id  = Genres.id
               GROUP BY Genres.id
               ORDER BY cnt DESC LIMIT 5"""
        ).fetchall()
        return [(r[0], r[1]) for r in rows]

    def _lease_rows(self, raw) -> list:
        result = []
        for r in raw:
            r = dict(r)
            result.append((
                r.get("full_name", ""),
                r.get("title", ""),
                r.get("issue_date", ""),
                r.get("return_deadline", ""),
                r.get("id"),       # lease_id
                r.get("user_id"),
                r.get("book_id"),
            ))
        return result

    def refresh(self):
        for w in self.winfo_children():
            w.destroy()
        self._icons = []
        _plt.close("all")
        self._build()

    def rebuild(self):
        self.refresh()

    def _make_lease_row(self, frame, row_data, col_configs=None):
        full_name, title, issue_date, return_deadline, lease_id, user_id, book_id = row_data

        for i, cfg in enumerate(self._lease_col_configs):
            frame.grid_columnconfigure(i, **cfg)

        frame.configure(cursor="hand2")

        lbl0 = ctk.CTkLabel(frame, text=full_name, anchor="w")
        lbl0.grid(row=0, column=0, sticky="ew", padx=(12, 0), pady=6)
        lbl1 = ctk.CTkLabel(frame, text=title, anchor="w", text_color="gray")
        lbl1.grid(row=0, column=1, sticky="ew", padx=(8, 0), pady=6)
        lbl2 = ctk.CTkLabel(frame, text=issue_date or "—", anchor="w")
        lbl2.grid(row=0, column=2, sticky="ew", padx=(8, 0), pady=6)
        lbl3 = ctk.CTkLabel(frame, text=return_deadline or "—", anchor="w")
        lbl3.grid(row=0, column=3, sticky="ew", padx=(8, 0), pady=6)

        open_cmd = lambda d=row_data: self._open_lease_popup(d)
        for w in (frame, lbl0, lbl1, lbl2, lbl3):
            w.bind("<Button-1>", lambda e, cmd=open_cmd: cmd())

    def _open_lease_popup(self, row_data):
        key = row_data[4]  # lease_id
        attr = f"_lease_win_{key}"
        win = getattr(self, attr, None)
        if win is None or not win.winfo_exists():
            setattr(self, attr, LeaseViewPopup(
                self.winfo_toplevel(), self.db, self.i18n,
                row_data, self.controller, self.refresh,
            ))
        else:
            win.focus()

    # ─────────────────────────── WIDGETS ───────────────────────────

    def _card(self, parent, title: str, value: str, row: int, col: int, icon_path: str):
        frame = ctk.CTkFrame(
            parent, fg_color=cons.CARD, corner_radius=15,
            border_width=2, border_color=cons.BLUE,
        )
        frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

        try:
            img = ctk.CTkImage(light_image=Image.open(icon_path), size=(100, 80))
            ctk.CTkLabel(frame, image=img, text="").grid(
                row=0, column=0, rowspan=2, padx=(30, 40), pady=10, sticky="nsew"
            )
            self._icons.append(img)
        except Exception:
            pass

        ctk.CTkLabel(frame, text=title, font=("Arial", 20)).grid(
            row=0, column=1, padx=10, pady=(10, 5), sticky="nsew"
        )
        ctk.CTkLabel(frame, text=value, font=("Arial", 64, "bold")).grid(
            row=1, column=1, padx=10, pady=(5, 10), sticky="nsew"
        )

    @staticmethod
    def _attach_debounced_resize(tk_widget, canvas, delay_ms=150):
        """Debounce the expensive canvas.draw() that matplotlib fires on every
        <Configure> resize pixel. matplotlib's own _resize handler keeps running
        (it correctly manages the internal PhotoImage buffer); only the Agg render
        step is deferred until the user stops resizing.
        """
        _original_draw = canvas.draw
        _timer = [None]

        def _debounced_draw():
            if _timer[0] is not None:
                tk_widget.after_cancel(_timer[0])
            _timer[0] = tk_widget.after(delay_ms, _original_draw)

        canvas.draw = _debounced_draw

    def _chart_genres(self, parent, data: list, row: int, col: int, rowspan: int = 1):
        frame = ctk.CTkFrame(parent, fg_color=cons.CARD, corner_radius=15)
        frame.grid(row=row, column=col, rowspan=rowspan, padx=10, pady=10, sticky="nsew")

        names  = [d[0] for d in data]
        counts = [d[1] for d in data]
        colors = [cons.BLUE, cons.ACCENT, cons.BLUE_ACTIVE, "#8fdb6e", "#d4c5f9"]

        fig = Figure(figsize=(3.5, 2.4), facecolor=cons.CARD)
        ax  = fig.add_subplot(111, facecolor=cons.CARD)

        if names:
            ax.pie(
                counts,
                labels=names,
                colors=colors[: len(names)],
                wedgeprops=dict(width=0.5),
                startangle=90,
                textprops={"fontsize": 8, "color": cons.TEXT},
            )
        else:
            ax.text(0.5, 0.5, "—", ha="center", va="center",
                    transform=ax.transAxes, color=cons.TEXT, fontsize=14)

        ax.set_title(self.i18n.t("table.catalog"), fontsize=9, color=cons.TEXT, pad=4)
        fig.tight_layout(pad=0.5)

        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        tk_w = canvas.get_tk_widget()
        tk_w.pack(fill="both", expand=True, padx=8, pady=8)
        self._attach_debounced_resize(tk_w, canvas)

    def _chart_monthly(self, parent, data: list, row: int, col: int, rowspan: int = 1):
        frame = ctk.CTkFrame(parent, fg_color=cons.CARD, corner_radius=15)
        frame.grid(row=row, column=col, rowspan=rowspan, padx=10, pady=10, sticky="nsew")

        months = [d[0] for d in data]
        counts = [d[1] for d in data]

        fig = Figure(figsize=(3.5, 2.4), facecolor=cons.CARD)
        ax  = fig.add_subplot(111, facecolor=cons.CARD)

        if months:
            ax.bar(months, counts, color=cons.BLUE, width=0.5)
            ax.tick_params(axis="x", rotation=30, labelsize=8, colors=cons.TEXT)
        else:
            ax.text(0.5, 0.5, "—", ha="center", va="center",
                    transform=ax.transAxes, color=cons.TEXT, fontsize=14)

        ax.tick_params(axis="y", labelsize=8, colors=cons.TEXT)
        ax.spines[["top", "right"]].set_visible(False)
        ax.spines[["bottom", "left"]].set_color(cons.TEXT)
        fig.tight_layout(pad=0.8)

        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        tk_w = canvas.get_tk_widget()
        tk_w.pack(fill="both", expand=True, padx=8, pady=8)
        self._attach_debounced_resize(tk_w, canvas)
