import customtkinter as ctk
from PIL import Image
import constantes as cons, tables

class MainPage(ctk.CTkFrame):
    def __init__(self, parent, db, controller):
        super().__init__(parent)
        self.db = db

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.main_page()

    def main_page(self):
        container = ctk.CTkFrame(self, fg_color=cons.BG)
        container.grid(row=1, column=0, sticky="nsew")

        container.grid_columnconfigure((1, 2, 3, 4), weight=10)
        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(2, weight=1)

        self.card(container, "books on hands", "607", 0, 0, "image/on_hand.png", 80, 2)
        self.card(container, "new readers", "1436", 0, 1, "image/reader.png", 80, 2)

        self.chart(container, "User statistics", 1, 0, 2, 2)
        self.chart(container, "books...", 3, 0, 2, 2)

        columns = ["Book", "ID", "Expire Date"]
        version1 = [(f"Book {i}", f"ID {i}", f"2026-0{i % 12 + 1}-01") for i in range(20)]
        version2 = [(f"Reader {i}", f"R-{i}", f"2026-0{i % 12 + 1}-15") for i in range(20)]
        version3 = [(f"Admin {i}", f"A-{i}", f"2026-0{i % 12 + 1}-20") for i in range(20)]

        table = tables.ScrollTable(container, columns, [version1, version2, version3], table_color=cons.CARD)
        table.grid(row=2, column=0, columnspan=5, sticky="nsew", padx=10, pady=10)


    def card(self, parent, title, value, col, row, icon_path, size, icon_rowspan):
        frame = ctk.CTkFrame(parent, fg_color=cons.CARD, corner_radius=15)
        frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

        icon = ctk.CTkImage(light_image=Image.open(icon_path), size=(size+20, size))

        icon_label = ctk.CTkLabel(frame, image=icon, text="")
        icon_label.grid(row=0, column=0, rowspan=icon_rowspan, padx=(30, 40), pady=10, sticky="nsew")

        title_label = ctk.CTkLabel(frame, text=title, font=("Arial", 20))
        title_label.grid(row=0, column=1, padx=10, pady=(10, 5), sticky="nsew")

        value_label = ctk.CTkLabel(frame, text=value, font=("Arial", 64, "bold"))
        value_label.grid(row=1, column=1, padx=10, pady=(5, 10), sticky="nsew")

        self.icon = icon


    def chart(self, parent, title, col, row, rowspan, colspan):
        frame = ctk.CTkFrame(parent, fg_color=cons.CARD, corner_radius=15)
        frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew", rowspan=rowspan, columnspan=colspan)

        ctk.CTkLabel(frame, text=title, font=("Arial", 14)).pack(pady=10)

        for i in range(6):
            bar = ctk.CTkFrame(
                frame,
                width=20,
                height=40 + i * 10,
                fg_color=cons.ACCENT if i % 2 == 0 else cons.BLUE
            )
            bar.pack(side="left", padx=5, pady=20, expand=True)
