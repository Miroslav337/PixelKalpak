import customtkinter as ctk
import platform, constantes as cons

class TopLevel(ctk.CTkToplevel):
    def __init__(self, master, title="Окно", width=300, height=200):
        super().__init__(master)

        self.title(title)
        self.width = width
        self.height = height

        self.overrideredirect(True)

        current_os = platform.system()
        if current_os == "Darwin":
            self.attributes('-type', 'dialog')

        master.update_idletasks()
        x = master.winfo_rootx() + (master.winfo_width() // 2) - (self.width // 2)
        y = master.winfo_rooty() + (master.winfo_height() // 2) - (self.height // 2)
        self.geometry(f"{self.width}x{self.height}+{x}+{y}")



        self.attributes('-topmost', True)
        self.bind("<Escape>", lambda e: self.on_close())
        self.focus_set()
        self.grab_set()

        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True)

    def on_close(self):
        self.grab_release()
        self.destroy()