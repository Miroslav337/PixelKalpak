import customtkinter as ctk
from PIL import Image
import constantes as cons

class ScrollTable(ctk.CTkFrame):
    def __init__(self, parent, columns, data_versions, table_color=cons.CARD):
        super().__init__(parent, fg_color=table_color, corner_radius=15)

        self.columns = columns
        self.data_versions = data_versions
        self.current_version = 0
        self.rows = []

        text = ["Active", "Expired", "Catalog"]

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        btn_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        for i in range(len(data_versions)):
            btn = ctk.CTkButton(
                btn_frame,
                text=text[i],
                width=10,
                command=lambda v=i: self.load_version(v),
                fg_color=cons.BLUE,
                hover_color=cons.BLUE_ACTIVE
            )
            btn.grid(row=0, column=i, padx=5, sticky="ew")

        search = ctk.CTkEntry(btn_frame, placeholder_text="🔍search")
        search.grid(row=0, column=3, padx=5, sticky="ew")

        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=1, column=0, sticky="ew", padx=5)
        header_frame.grid_columnconfigure((0, 1, 2), weight=1)
        for i, col_name in enumerate(columns):
            ctk.CTkLabel(header_frame, text=col_name, font=("Arial", 14, "bold")).grid(row=0, column=i, padx=10, pady=5, sticky="ew")

        self.scroll = ctk.CTkScrollableFrame(self, fg_color=cons.BG)
        self.scroll.grid(row=2, column=0, sticky="nsew", padx=5, pady=5, columnspan=5)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.load_version(0)

    def add_row(self, row_data):
        row_frame = ctk.CTkFrame(self.scroll, fg_color="transparent")
        row_frame.pack(fill="x", pady=2)

        for i in range(len(row_data)):
            row_frame.grid_columnconfigure(i, weight=1)

        for i, value in enumerate(row_data):
            label = ctk.CTkLabel(row_frame, text=value)
            label.grid(row=0, column=i, sticky="ew", padx=10)

        self.rows.append(row_frame)

    def clear(self):
        for r in self.rows:
            r.destroy()
        self.rows = []

    def load_version(self, version_index):
        self.current_version = version_index
        self.clear()
        for item in self.data_versions[version_index]:
            self.add_row(item)