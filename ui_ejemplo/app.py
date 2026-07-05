import customtkinter as ctk
from PIL import Image
import os
from ui.styles.theme import apply_theme
from ui.views.menu_principal import MenuPrincipal
from ui.views.control_dual import ControlDualVista


class AplicacionControles(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Aplicación de Automatización")
        self.geometry("900x700")
        self.resizable(False, False)
        self.configure(fg_color="black")

        colors = apply_theme()

        UI_DIR = os.path.dirname(os.path.abspath(__file__))
        IMG_PATH = os.path.join(UI_DIR, "assets", "trazo-onda-12.png")
        LOGO_PATH = os.path.join(UI_DIR, "assets", "icon.ico")

        self.iconbitmap(LOGO_PATH)

        imagen = Image.open(IMG_PATH)

        self.bg_image = ctk.CTkImage(
            light_image=imagen,
            dark_image=imagen,
            size=(900, 700)
        )

        self.bg_label = ctk.CTkLabel(
            self,
            image=self.bg_image,
            text="",
            fg_color="black"
        )
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        self.menu_principal = MenuPrincipal(self, colors, self)
        self.control_dual = ControlDualVista(self, colors, self)

        self.mostrar_menu()

    def ocultar_frames(self):
        self.menu_principal.place_forget()
        self.control_dual.place_forget()

    def mostrar_menu(self):
        self.ocultar_frames()
        self.menu_principal.place(relx=0.5, rely=0.5, anchor="center")

    def mostrar_control_dual(self):
        self.ocultar_frames()
        self.control_dual.place(relx=0.5, rely=0.5, anchor="center")


if __name__ == "__main__":
    app = AplicacionControles()
    app.mainloop()