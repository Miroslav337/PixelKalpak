import customtkinter as ctk
import constantes as cons

class TopLevel(ctk.CTkToplevel):
    def __init__(self, master, title="Окно", width=300, height=200, parent_popup=None):
        self._parent_popup = parent_popup
        self._restore_parent = True

        if parent_popup is None:
            # Standalone popup: close any existing active popup
            root = master.winfo_toplevel()
            existing = getattr(root, '_active_popup', None)
            if existing is not None and existing.winfo_exists():
                existing.destroy()

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
            try:
                self.nametowidget(".")._active_popup = self
            except Exception:
                pass
        else:
            # Child popup: release parent's grab and hide it
            if parent_popup.winfo_exists():
                try:
                    parent_popup.grab_release()
                except Exception:
                    pass
                parent_popup.withdraw()

        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True)

        self.after_idle(self._safe_grab)

    def _safe_grab(self):
        try:
            self.grab_set()
        except Exception:
            pass

    def on_close(self):
        self.grab_release()
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
            try:
                root = self.nametowidget(".")
                if getattr(root, '_active_popup', None) is self:
                    root._active_popup = None
            except Exception:
                pass
        self.destroy()
