import customtkinter as ctk
from PIL import Image
import mainpage, user, admin, profile, constantes as cons

ctk.set_appearance_mode("light")



class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.geometry("1200x720")
        self.configure(fg_color=cons.BG)
        self.title("Library")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.topbar()

        container = ctk.CTkFrame(self)
        container.grid(row=1, column=0, sticky="nsew")

        container.grid_rowconfigure(1, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.pages = {}

        for Page in (mainpage.MainPage, user.UsersPage, admin.AdminPage, profile.LogInPage):
            page = Page(container)
            self.pages[Page] = page

            page.grid(row=1, column=0, sticky="nsew")

        self.show_page(mainpage.MainPage)

    def topbar(self):
        frame = ctk.CTkFrame(self, height=60, fg_color=cons.CARD, corner_radius=15)
        frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)

        frame.grid_columnconfigure(0, weight=0)
        frame.grid_columnconfigure(1, weight=1)
        frame.grid_columnconfigure(2, weight=0)
        frame.grid_columnconfigure(3, weight=0)

        logo_img = ctk.CTkImage(
            light_image=Image.open("image/logo.jpg"),
            size=(40, 40)
        )

        logo_label = ctk.CTkLabel(frame, image=logo_img, text="")
        logo_label.grid(row=0, column=0, padx=15, sticky="w")

        pixel = ctk.CTkLabel(frame, text="Pixel Kalpak", font=("Arial", 20))
        pixel.grid(row=0, column=1, padx=10, pady=(10, 5), sticky="w")

        nav_frame = ctk.CTkFrame(frame, fg_color="transparent")
        nav_frame.grid(row=0, column=2, sticky="ew")

        buttons = [
            ("main page", mainpage.MainPage),
            ("admin", admin.AdminPage),
            ("users", user.UsersPage),
        ]

        for text, page in buttons:

            btn = ctk.CTkButton(
                nav_frame,
                text=text,
                fg_color="transparent",
                text_color="black",
                hover_color=cons.GRAY,
                command=lambda p=page: self.show_page(p)
            )
            btn.grid(row=0, column=buttons.index((text, page)), padx=5)

        login = ctk.CTkButton(frame, text="log in", width=100, border_spacing=10, fg_color=cons.BLUE, text_color="black", hover_color=cons.BLUE_ACTIVE, command=lambda p=profile.LogInPage: self.show_page(p))
        login.grid(row=0, column=3, padx=15, sticky="e")

        self.logo_img = logo_img


    def show_page(self, page_class):
        self.pages[page_class].tkraise()

if __name__ == "__main__":
    app = App()
    app.mainloop()