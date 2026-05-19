import customtkinter as ctk
import constantes as cons
from settings import ACCENT_PRESETS
from top_labels import AddAdminPopup, ChangePasswordPopup, ConfirmDeletePopup


class LogInPage(ctk.CTkFrame):
    def __init__(self, parent, db, i18n, controller):
        super().__init__(parent)
        self.db = db
        self.i18n = i18n
        self.controller = controller
        self.configure(fg_color=cons.BG)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build()

    def _build(self):
        card = ctk.CTkFrame(self, fg_color=cons.CARD, corner_radius=16)
        card.grid(row=0, column=0)
        card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            card, text=self.i18n.t("page.login"), font=("Arial", 22, "bold")
        ).grid(row=0, column=0, padx=60, pady=(30, 20))

        ctk.CTkLabel(card, text=self.i18n.t("label.username"), anchor="w").grid(
            row=1, column=0, padx=40, sticky="w"
        )
        self.username_entry = ctk.CTkEntry(card, width=280)
        self.username_entry.grid(row=2, column=0, padx=40, pady=(4, 12))

        ctk.CTkLabel(card, text=self.i18n.t("label.password"), anchor="w").grid(
            row=3, column=0, padx=40, sticky="w"
        )
        self.password_entry = ctk.CTkEntry(card, width=280, show="*")
        self.password_entry.grid(row=4, column=0, padx=40, pady=(4, 4))

        self.error_label = ctk.CTkLabel(card, text="", text_color="red")
        self.error_label.grid(row=5, column=0, padx=40, pady=(2, 4))

        ctk.CTkButton(
            card,
            text=self.i18n.t("btn.login"),
            fg_color=cons.BLUE,
            hover_color=cons.BLUE_ACTIVE,
            text_color="black",
            width=280,
            command=self._login,
        ).grid(row=6, column=0, padx=40, pady=(4, 30))

        self.username_entry.bind("<Return>", lambda e: self._login())
        self.password_entry.bind("<Return>", lambda e: self._login())

    def rebuild(self):
        for w in self.winfo_children():
            w.destroy()
        self._build()

    def _login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get()

        if not username or not password:
            self.error_label.configure(text=self.i18n.t("msg.field_required"))
            return

        if self.db.check_admin_password(username, password):
            admin_row = self.db.get_admin(username)
            self.controller.set_authorized({
                "id": admin_row["id"],
                "username": admin_row["username"],
                "role": admin_row["role"],
            })
            self.error_label.configure(text="")
            self.username_entry.delete(0, "end")
            self.password_entry.delete(0, "end")
        else:
            self.error_label.configure(text=self.i18n.t("msg.login_error"))


class ProfilePage(ctk.CTkFrame):
    def __init__(self, parent, db, i18n, controller):
        super().__init__(parent)
        self.db = db
        self.i18n = i18n
        self.controller = controller
        self.configure(fg_color=cons.BG)

        self._lang_btns = {}
        self._theme_btns = {}
        self._accent_btns = {}

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build()

    # ─────────────────────────── BUILD ─────────────────────────────

    def _build(self):
        outer = ctk.CTkFrame(self, fg_color=cons.BG)
        outer.grid(row=0, column=0, sticky="nsew", padx=30, pady=20)
        outer.grid_columnconfigure(0, weight=1)
        outer.grid_columnconfigure(1, weight=2)
        outer.grid_rowconfigure(0, weight=1)

        # ── Left: profile card ───────────────────────────────────────
        left = ctk.CTkFrame(outer, fg_color=cons.CARD, corner_radius=16)
        left.grid(row=0, column=0, sticky="n", padx=(0, 12))
        left.grid_columnconfigure(0, weight=1)

        avatar = ctk.CTkFrame(left, width=72, height=72, corner_radius=36, fg_color=cons.BLUE)
        avatar.grid(row=0, column=0, pady=(28, 12))
        avatar.grid_propagate(False)
        ctk.CTkLabel(avatar, text="👤", font=("Arial", 28)).place(relx=0.5, rely=0.5, anchor="center")

        self._name_label = ctk.CTkLabel(left, text="—", font=("Arial", 18, "bold"))
        self._name_label.grid(row=1, column=0, padx=40, pady=(0, 4))

        self._role_label = ctk.CTkLabel(left, text="", font=("Arial", 13), text_color=cons.BLUE_ACTIVE)
        self._role_label.grid(row=2, column=0, padx=40, pady=(0, 20))

        ctk.CTkButton(
            left,
            text=self.i18n.t("popup.change_password"),
            fg_color=cons.BLUE,
            hover_color=cons.BLUE_ACTIVE,
            text_color="black",
            width=200,
            command=self._change_own_password,
        ).grid(row=3, column=0, padx=40, pady=(0, 8))

        ctk.CTkButton(
            left,
            text=self.i18n.t("btn.logout"),
            fg_color="transparent",
            border_width=1,
            border_color="#d95050",
            text_color="#d95050",
            hover_color="#ffd0d0",
            width=200,
            command=self.controller.set_logged_out,
        ).grid(row=4, column=0, padx=40, pady=(0, 28))

        # ── Right: settings + admins ─────────────────────────────────
        self._right = ctk.CTkFrame(outer, fg_color="transparent")
        self._right.grid(row=0, column=1, sticky="nsew", padx=(12, 0))
        self._right.grid_columnconfigure(0, weight=1)

        self._build_settings_card()

    def _build_settings_card(self):
        card = ctk.CTkFrame(self._right, fg_color=cons.CARD, corner_radius=16)
        card.grid(row=0, column=0, sticky="ew")
        card.grid_columnconfigure(1, weight=1)

        # Language
        ctk.CTkLabel(card, text=self.i18n.t("label.language"), font=("Arial", 14)).grid(
            row=0, column=0, padx=(30, 20), pady=(24, 14), sticky="w"
        )
        lang_row = ctk.CTkFrame(card, fg_color="transparent")
        lang_row.grid(row=0, column=1, padx=(0, 30), pady=(24, 14), sticky="e")

        for code in ("ru", "en", "ky"):
            active = self.controller.settings.language == code
            btn = ctk.CTkButton(
                lang_row, text=code.upper(), width=56,
                fg_color=cons.BLUE_ACTIVE if active else "transparent",
                border_width=1, border_color=cons.BLUE,
                text_color=cons.TEXT, hover_color=cons.GRAY,
                command=lambda c=code: self._set_lang(c),
            )
            btn.pack(side="left", padx=3)
            self._lang_btns[code] = btn

        ctk.CTkFrame(card, height=1, fg_color="gray80").grid(
            row=1, column=0, columnspan=2, sticky="ew", padx=20
        )

        # Theme
        ctk.CTkLabel(card, text=self.i18n.t("label.theme"), font=("Arial", 14)).grid(
            row=2, column=0, padx=(30, 20), pady=14, sticky="w"
        )
        theme_row = ctk.CTkFrame(card, fg_color="transparent")
        theme_row.grid(row=2, column=1, padx=(0, 30), pady=14, sticky="e")

        for mode, key in (("light", "label.light"), ("dark", "label.dark")):
            active = self.controller.settings.theme == mode
            btn = ctk.CTkButton(
                theme_row, text=self.i18n.t(key), width=80,
                fg_color=cons.BLUE_ACTIVE if active else "transparent",
                border_width=1, border_color=cons.BLUE,
                text_color=cons.TEXT, hover_color=cons.GRAY,
                command=lambda m=mode: self._set_theme(m),
            )
            btn.pack(side="left", padx=3)
            self._theme_btns[mode] = btn

        ctk.CTkFrame(card, height=1, fg_color="gray80").grid(
            row=3, column=0, columnspan=2, sticky="ew", padx=20
        )

        # Accent
        ctk.CTkLabel(card, text=self.i18n.t("label.accent"), font=("Arial", 14)).grid(
            row=4, column=0, padx=(30, 20), pady=(14, 24), sticky="w"
        )
        accent_row = ctk.CTkFrame(card, fg_color="transparent")
        accent_row.grid(row=4, column=1, padx=(0, 30), pady=(14, 24), sticky="e")

        for name, colors in ACCENT_PRESETS.items():
            active = self.controller.settings.accent == name
            btn = ctk.CTkButton(
                accent_row, text="", width=40, height=40, corner_radius=20,
                fg_color=colors["BLUE"],
                hover_color=colors["BLUE_ACTIVE"],
                border_width=3 if active else 0,
                border_color="black",
                command=lambda n=name: self._set_accent(n),
            )
            btn.pack(side="left", padx=4)
            self._accent_btns[name] = btn

        ctk.CTkFrame(card, height=1, fg_color="gray80").grid(
            row=5, column=0, columnspan=2, sticky="ew", padx=20
        )

        ctk.CTkLabel(card, text=self.i18n.t("label.loan_days"), font=("Arial", 14)).grid(
            row=6, column=0, padx=(30, 20), pady=(14, 24), sticky="w"
        )
        loan_ctrl = ctk.CTkFrame(card, fg_color="transparent")
        loan_ctrl.grid(row=6, column=1, padx=(0, 30), pady=(14, 24), sticky="e")

        vcmd = (card.register(lambda v: v == "" or (v.isdigit() and len(v) <= 4)), "%P")
        self._loan_entry = ctk.CTkEntry(
            loan_ctrl, width=70,
            validate="key", validatecommand=vcmd,
        )
        self._loan_entry.insert(0, str(self.controller.settings.loan_days))
        self._loan_entry.pack(side="left", padx=(0, 6))

        ctk.CTkButton(
            loan_ctrl, text=self.i18n.t("btn.save"), width=80,
            fg_color=cons.BLUE, hover_color=cons.BLUE_ACTIVE, text_color="black",
            command=self._save_loan_days,
        ).pack(side="left")

    # ─────────────────────────── ADMINS SECTION ─────────────────────

    def _render_admins(self):
        if hasattr(self, "_admins_card") and self._admins_card.winfo_exists():
            self._admins_card.destroy()

        admin = self.controller.current_admin
        if not admin or admin.get("role") != "superadmin":
            return

        self._admins_card = ctk.CTkFrame(self._right, fg_color=cons.CARD, corner_radius=16)
        self._admins_card.grid(row=1, column=0, sticky="ew", pady=(12, 0))
        self._admins_card.grid_columnconfigure(0, weight=1)

        # Header row
        hdr = ctk.CTkFrame(self._admins_card, fg_color="transparent")
        hdr.grid(row=0, column=0, sticky="ew", padx=20, pady=(18, 8))
        hdr.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            hdr, text=self.i18n.t("section.admins"),
            font=("Arial", 14, "bold"), anchor="w",
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkButton(
            hdr, text="+ " + self.i18n.t("btn.add"),
            width=110, height=30,
            fg_color=cons.ACCENT, hover_color="#8fdb6e", text_color="black",
            command=self._add_admin,
        ).grid(row=0, column=1, sticky="e")

        ctk.CTkFrame(
            self._admins_card, height=1, fg_color="gray80"
        ).grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 4))

        # Admin rows
        admins = self.db.get_all_admins()
        for i, a in enumerate(admins):
            row_frame = ctk.CTkFrame(self._admins_card, fg_color="transparent")
            row_frame.grid(row=i + 2, column=0, sticky="ew", padx=20, pady=3)
            row_frame.grid_columnconfigure(0, weight=1)

            role_color = cons.BLUE_ACTIVE if a["role"] == "superadmin" else "gray"
            ctk.CTkLabel(
                row_frame, text=a["username"],
                font=("Arial", 13), anchor="w",
            ).grid(row=0, column=0, sticky="w")

            ctk.CTkLabel(
                row_frame, text=a["role"],
                font=("Arial", 11), text_color=role_color, anchor="w",
            ).grid(row=0, column=1, sticky="w", padx=(8, 12))

            ctk.CTkButton(
                row_frame, text="🔑", width=30, height=24,
                fg_color=cons.BLUE, hover_color=cons.BLUE_ACTIVE, text_color="black",
                command=lambda aid=a["id"], uname=a["username"]: self._change_admin_password(aid, uname),
            ).grid(row=0, column=2, sticky="e", padx=(0, 4))

            is_self = admin["id"] == a["id"]
            ctk.CTkButton(
                row_frame, text="−", width=28, height=24,
                fg_color="#d95050" if not is_self else cons.GRAY,
                hover_color="#b03030" if not is_self else cons.GRAY,
                text_color="white", font=("Arial", 14, "bold"),
                state="normal" if not is_self else "disabled",
                command=lambda aid=a["id"], uname=a["username"]: self._delete_admin(aid, uname),
            ).grid(row=0, column=3, sticky="e")

        bottom_pad = ctk.CTkFrame(self._admins_card, fg_color="transparent", height=10)
        bottom_pad.grid(row=len(admins) + 2, column=0)

    def _change_own_password(self):
        admin = self.controller.current_admin
        if not admin:
            return
        current = getattr(self, "_change_pw_win", None)
        if current is None or not current.winfo_exists():
            self._change_pw_win = ChangePasswordPopup(
                self.winfo_toplevel(), self.db, self.i18n,
                admin["id"], admin["username"], require_current=True,
            )
        else:
            current.focus()

    def _change_admin_password(self, admin_id: int, username: str):
        current = getattr(self, "_change_other_pw_win", None)
        if current is None or not current.winfo_exists():
            self._change_other_pw_win = ChangePasswordPopup(
                self.winfo_toplevel(), self.db, self.i18n,
                admin_id, username, require_current=False,
            )
        else:
            current.focus()

    def _add_admin(self):
        current = getattr(self, "_add_admin_win", None)
        if current is None or not current.winfo_exists():
            self._add_admin_win = AddAdminPopup(
                self.winfo_toplevel(), self.db, self.i18n, self._render_admins
            )
        else:
            current.focus()

    def _delete_admin(self, admin_id: int, username: str):
        current = getattr(self, "_confirm_admin_win", None)
        if current is None or not current.winfo_exists():
            self._confirm_admin_win = ConfirmDeletePopup(
                self.winfo_toplevel(), self.i18n, username,
                lambda: self._do_delete_admin(admin_id),
            )
        else:
            current.focus()

    def _do_delete_admin(self, admin_id: int):
        try:
            self.db.delete_admin(admin_id)
        except ValueError:
            pass
        self._render_admins()

    def rebuild(self):
        for w in self.winfo_children():
            w.destroy()
        self._lang_btns = {}
        self._theme_btns = {}
        self._accent_btns = {}
        self._build()
        self.refresh()

    # ─────────────────────────── STATE ──────────────────────────────

    def refresh(self):
        admin = self.controller.current_admin
        if admin:
            self._name_label.configure(text=admin["username"])
            self._role_label.configure(text=admin["role"])
        else:
            self._name_label.configure(text="—")
            self._role_label.configure(text="")

        cur_lang = self.controller.settings.language
        for code, btn in self._lang_btns.items():
            btn.configure(fg_color=cons.BLUE_ACTIVE if code == cur_lang else "transparent")

        cur_theme = self.controller.settings.theme
        for mode, btn in self._theme_btns.items():
            btn.configure(fg_color=cons.BLUE_ACTIVE if mode == cur_theme else "transparent")

        cur_accent = self.controller.settings.accent
        for name, btn in self._accent_btns.items():
            btn.configure(border_width=3 if name == cur_accent else 0)

        self._render_admins()

    def _set_lang(self, lang: str):
        self.controller.i18n.set_lang(lang)
        self.controller.settings.set("language", lang)
        for code, btn in self._lang_btns.items():
            btn.configure(fg_color=cons.BLUE_ACTIVE if code == lang else "transparent")
        self.controller.rebuild_ui()

    def _set_theme(self, mode: str):
        ctk.set_appearance_mode(mode)
        self.controller.settings.set("theme", mode)
        palette = cons.DARK_COLORS if mode == "dark" else cons.LIGHT_COLORS
        cons.BG   = palette["BG"]
        cons.CARD = palette["CARD"]
        cons.GRAY = palette["GRAY"]
        cons.TEXT = palette["TEXT"]
        for m, btn in self._theme_btns.items():
            btn.configure(fg_color=cons.BLUE_ACTIVE if m == mode else "transparent")
        # delay so CTK finishes its own appearance-mode callbacks before we destroy widgets
        self.controller.after(80, self.controller.rebuild_ui)

    def _set_accent(self, name: str):
        self.controller.settings.set("accent", name)
        for n, btn in self._accent_btns.items():
            btn.configure(border_width=3 if n == name else 0)
        self.controller.apply_accent(name)

    def _save_loan_days(self):
        val = self._loan_entry.get().strip()
        days = int(val) if val.isdigit() and int(val) > 0 else 30
        self.controller.settings.set("loan_days", days)
        self._loan_entry.delete(0, "end")
        self._loan_entry.insert(0, str(days))
