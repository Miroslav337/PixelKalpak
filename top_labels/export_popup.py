import csv
import json
from tkinter import filedialog

from .top_level import TopLevel
import customtkinter as ctk
import constantes as cons

# Maps raw DB key → i18n key for human-readable column headers
_FIELD_I18N = {
    "full_name":         "label.full_name",
    "phone":             "label.phone",
    "gender":            "label.gender",
    "registration_date": "label.reg_date",
    "notes":             "label.notes",
    "is_active":         "label.active",
    "title":             "label.title",
    "author_name":       "label.author",
    "publisher":         "label.publisher",
    "year":              "label.year",
    "total_count":       "label.count",
    "available_count":   "label.available",
    "status":            "label.status",
    "issue_date":        "label.issue_date",
    "return_deadline":   "label.return_date",
}


class ExportPopup(TopLevel):
    def __init__(self, master, i18n, data: list, filename_hint: str = "export"):
        super().__init__(master, title=i18n.t("btn.export"), width=360, height=520)
        self.i18n = i18n
        self.data = [dict(r) if not isinstance(r, dict) else r for r in data]
        self.filename_hint = filename_hint
        self._build()

    # ── helpers ─────────────────────────────────────────────────────

    def _label_for(self, key: str) -> str:
        i18n_key = _FIELD_I18N.get(key)
        if i18n_key:
            return self.i18n.t(i18n_key)
        return key.upper() if key == "id" else key

    # ── build ────────────────────────────────────────────────────────

    def _build(self):
        title_bar = ctk.CTkFrame(
            self.main_frame, fg_color=cons.BLUE, corner_radius=0, height=40
        )
        title_bar.pack(fill="x")
        title_bar.pack_propagate(False)
        ctk.CTkLabel(
            title_bar, text=self.i18n.t("btn.export"),
            font=("Arial", 14, "bold"), text_color="black",
        ).pack(side="left", padx=12, pady=8)
        ctk.CTkButton(
            title_bar, text="✕", width=32, height=28,
            fg_color="transparent", hover_color="#d95050", text_color="black",
            command=self.on_close,
        ).pack(side="right", padx=4, pady=4)

        if not self.data:
            ctk.CTkLabel(self.main_frame, text="—", text_color="gray").pack(pady=40)
            return

        form = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=16, pady=12)
        form.grid_columnconfigure(1, weight=1)

        r = 0

        # ── Format ──────────────────────────────────────────────────
        ctk.CTkLabel(form, text=self.i18n.t("label.format"), anchor="w").grid(
            row=r, column=0, sticky="w", padx=(0, 12), pady=(0, 6)
        )
        self._fmt_var = ctk.StringVar(value="CSV")
        ctk.CTkOptionMenu(
            form, variable=self._fmt_var,
            values=["CSV", "TXT", "XLSX", "JSON"],
            fg_color=cons.CARD, button_color=cons.BLUE,
            button_hover_color=cons.BLUE_ACTIVE, text_color="black",
            command=self._on_fmt_change,
        ).grid(row=r, column=1, sticky="ew", pady=(0, 6))
        r += 1

        # ── Separator ───────────────────────────────────────────────
        ctk.CTkLabel(form, text=self.i18n.t("label.separator"), anchor="w").grid(
            row=r, column=0, sticky="w", padx=(0, 12), pady=(0, 10)
        )
        self._sep_var = ctk.StringVar(value=",")
        self._sep_menu = ctk.CTkOptionMenu(
            form, variable=self._sep_var,
            values=[",", ";", "Tab"],
            fg_color=cons.CARD, button_color=cons.BLUE,
            button_hover_color=cons.BLUE_ACTIVE, text_color="black",
        )
        self._sep_menu.grid(row=r, column=1, sticky="ew", pady=(0, 10))
        r += 1

        # ── Fields header ────────────────────────────────────────────
        hdr = ctk.CTkFrame(form, fg_color=cons.ACCENT, corner_radius=6, height=28)
        hdr.grid(row=r, column=0, columnspan=2, sticky="ew", pady=(0, 6))
        hdr.grid_propagate(False)
        ctk.CTkLabel(
            hdr, text=self.i18n.t("label.fields"),
            font=("Arial", 12, "bold"), text_color="black",
        ).pack(side="left", padx=10)
        r += 1

        # ── Checkboxes ───────────────────────────────────────────────
        scroll = ctk.CTkScrollableFrame(form, fg_color="transparent", height=160)
        scroll.grid(row=r, column=0, columnspan=2, sticky="ew", pady=(0, 8))
        r += 1

        self._field_vars: dict[str, ctk.BooleanVar] = {}
        for key in self.data[0].keys():
            var = ctk.BooleanVar(value=True)
            self._field_vars[key] = var
            ctk.CTkCheckBox(
                scroll,
                text=self._label_for(key),
                variable=var,
                fg_color=cons.BLUE, hover_color=cons.BLUE_ACTIVE,
                checkmark_color="black",
            ).pack(anchor="w", padx=6, pady=3)

        # ── Error ────────────────────────────────────────────────────
        self._error = ctk.CTkLabel(form, text="", text_color="red", anchor="w")
        self._error.grid(row=r, column=0, columnspan=2, sticky="w", pady=(0, 4))
        r += 1

        # ── Buttons ──────────────────────────────────────────────────
        btn_frame = ctk.CTkFrame(form, fg_color="transparent")
        btn_frame.grid(row=r, column=0, columnspan=2, sticky="ew")
        btn_frame.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(
            btn_frame, text=self.i18n.t("btn.cancel"),
            fg_color="transparent", border_width=1,
            text_color=cons.BLUE_ACTIVE, border_color=cons.BLUE_ACTIVE,
            command=self.on_close,
        ).grid(row=0, column=0, sticky="ew", padx=(0, 5))

        ctk.CTkButton(
            btn_frame, text=self.i18n.t("btn.export"),
            fg_color=cons.BLUE, hover_color=cons.BLUE_ACTIVE, text_color="black",
            command=self._export,
        ).grid(row=0, column=1, sticky="ew", padx=(5, 0))

    # ── events ───────────────────────────────────────────────────────

    def _on_fmt_change(self, value: str):
        state = "disabled" if value in ("XLSX", "JSON") else "normal"
        self._sep_menu.configure(state=state)

    # ── export ────────────────────────────────────────────────────────

    def _export(self):
        selected_keys = [k for k, v in self._field_vars.items() if v.get()]
        if not selected_keys:
            self._error.configure(text=self.i18n.t("msg.field_required"))
            return

        headers = [self._label_for(k) for k in selected_keys]
        fmt = self._fmt_var.get()

        ext_map  = {"CSV": ".csv", "TXT": ".txt", "XLSX": ".xlsx", "JSON": ".json"}
        type_map = {
            "CSV":  [("CSV files",   "*.csv")],
            "TXT":  [("Text files",  "*.txt")],
            "XLSX": [("Excel files", "*.xlsx")],
            "JSON": [("JSON files",  "*.json")],
        }

        path = filedialog.asksaveasfilename(
            defaultextension=ext_map[fmt],
            filetypes=type_map[fmt],
            initialfile=self.filename_hint,
        )
        if not path:
            return

        sep = {",": ",", ";": ";", "Tab": "\t"}.get(self._sep_var.get(), ",")

        if fmt == "CSV":
            with open(path, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f, delimiter=sep)
                writer.writerow(headers)
                for row in self.data:
                    writer.writerow([row.get(k, "") or "" for k in selected_keys])

        elif fmt == "TXT":
            with open(path, "w", encoding="utf-8") as f:
                for row in self.data:
                    line = sep.join(str(row.get(k, "") or "") for k in selected_keys)
                    f.write(line + "\n")

        elif fmt == "XLSX":
            try:
                import openpyxl
            except ImportError:
                self._error.configure(text="openpyxl not installed: pip install openpyxl")
                return
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.append(headers)
            for row in self.data:
                ws.append([row.get(k, "") or "" for k in selected_keys])
            wb.save(path)

        else:  # JSON
            records = [{headers[i]: (row.get(k) or "") for i, k in enumerate(selected_keys)}
                       for row in self.data]
            with open(path, "w", encoding="utf-8") as f:
                json.dump(records, f, ensure_ascii=False, indent=2)

        self.on_close()
