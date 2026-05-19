import tkinter as tk
import customtkinter as ctk
import constantes as cons


class TopLevel(ctk.CTkToplevel):
    def __init__(self, master, title="Окно", width=300, height=200, parent_popup=None):
        self._parent_popup = parent_popup
        self._restore_parent = True
        self._app_root = master.winfo_toplevel()
        self._overlay = None
        self._overlay_binds = []

        if parent_popup is None:
            existing = getattr(self._app_root, '_active_popup', None)
            if existing is not None and existing.winfo_exists():
                existing.on_close()

        super().__init__(master)

        self.title(title)
        self.width = width
        self.height = height
        self.overrideredirect(True)

        master.update_idletasks()
        x = master.winfo_rootx() + (master.winfo_width() // 2) - (self.width // 2)
        y = master.winfo_rooty() + (master.winfo_height() // 2) - (self.height // 2)
        self.geometry(f"{self.width}x{self.height}+{x}+{y}")

        self.attributes('-topmost', True)
        self.bind("<Escape>", lambda e: self.on_close())
        self.focus_set()

        if parent_popup is None:
            self._app_root._active_popup = self
            self.after_idle(self._create_overlay)
        else:
            if parent_popup.winfo_exists():
                try:
                    parent_popup.grab_release()
                except Exception:
                    pass
                parent_popup.withdraw()
            self.after_idle(self._safe_grab)

        self.configure(fg_color=cons.CARD)
        self.main_frame = ctk.CTkFrame(
            self, fg_color=cons.CARD,
            border_width=2, border_color=cons.BLUE_ACTIVE,
        )
        self.main_frame.pack(fill="both", expand=True)

    # ── overlay (root-level popups) ───────────────────────────────────

    def _create_overlay(self):
        self._app_root.update_idletasks()

        # Transparent tk.Toplevel covering the client area only (below title bar).
        # winfo_rootx/y gives the client-area origin, so the title bar is NOT covered
        # and the system X button remains fully clickable.
        self._overlay = tk.Toplevel(self._app_root)
        self._overlay.overrideredirect(True)
        self._overlay.configure(bg="black")
        self._overlay.attributes("-alpha", 0.01)
        self._overlay.attributes("-topmost", True)
        self._sync_overlay()

        for btn in ("<Button-1>", "<Button-2>", "<Button-3>"):
            self._overlay.bind(btn, lambda e: self._bring_popup_to_front())

        bid = self._app_root.bind("<Configure>", self._on_root_configure, add=True)
        self._overlay_binds.append(("Configure", bid))

        self.lift()
        self.focus_force()

    def _sync_overlay(self):
        if self._overlay is None or not self._overlay.winfo_exists():
            return
        self._app_root.update_idletasks()
        x = self._app_root.winfo_rootx()
        y = self._app_root.winfo_rooty()
        w = self._app_root.winfo_width()
        h = self._app_root.winfo_height()
        self._overlay.geometry(f"{w}x{h}+{x}+{y}")

    def _on_root_configure(self, event=None):
        self._sync_overlay()
        self.lift()

    def _bring_popup_to_front(self):
        self.lift()
        self.focus_force()

    def _destroy_overlay(self):
        for event, bid in self._overlay_binds:
            try:
                self._app_root.unbind(event, bid)
            except Exception:
                pass
        self._overlay_binds.clear()
        if self._overlay is not None and self._overlay.winfo_exists():
            self._overlay.destroy()
        self._overlay = None

    # ── grab (child popups only) ──────────────────────────────────────

    def _safe_grab(self):
        try:
            self.grab_set()
        except Exception:
            pass

    # ── close ─────────────────────────────────────────────────────────

    def on_close(self):
        self._destroy_overlay()
        try:
            self.grab_release()
        except Exception:
            pass

        if self._parent_popup is not None:
            if self._parent_popup.winfo_exists():
                if self._restore_parent:
                    self._parent_popup.deiconify()
                    self._parent_popup.lift()
                    self._parent_popup.focus_set()
                    try:
                        self._parent_popup.grab_set()
                    except Exception:
                        pass
                else:
                    self._parent_popup._restore_parent = False
                    self._parent_popup.on_close()
        else:
            if getattr(self._app_root, '_active_popup', None) is self:
                self._app_root._active_popup = None

        self.destroy()
