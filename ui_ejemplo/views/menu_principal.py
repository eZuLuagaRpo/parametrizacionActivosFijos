import customtkinter as ctk
from ui.views.control_dual import ControlDualVista


class MenuPrincipal(ctk.CTkFrame):
    def __init__(self, master, colors, app):
        super().__init__(master, fg_color="transparent")

        self.colors = colors
        self.app = app

        self.grid(row=0, column=0, sticky="nsew")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        card = ctk.CTkFrame(
            self,
            fg_color=colors["card"],
            corner_radius=28,
            border_width=1,
            border_color=colors["border"]
        )
        card.grid(row=0, column=0)
        card.grid_propagate(False)
        card.configure(width=380, height=230)

        card.grid_rowconfigure((0, 1, 2, 3), weight=0)
        card.grid_columnconfigure(0, weight=1)

        marca = ctk.CTkLabel(
            card,
            text="Bancolombia",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=colors["dark"]
        )
        marca.grid(row=0, column=0, padx=24, pady=(22, 4), sticky="ew")

        title = ctk.CTkLabel(
            card,
            text="Aplicación de Automatización",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=colors["secondary"],
            wraplength=320,
            justify="center"
        )
        title.grid(row=1, column=0, padx=24, pady=(0, 18), sticky="ew")

        self.control_combo = ctk.CTkOptionMenu(
            card,
            values=["Control Dual"],
            width=300,
            height=38,
            corner_radius=12,
            fg_color=colors["white"],
            button_color=colors["dark"],
            button_hover_color=colors["hover_dark"],
            dropdown_fg_color=colors["white"],
            dropdown_hover_color=colors["yellow"],
            dropdown_text_color=colors["dark"],
            text_color=colors["dark"]
        )
        self.control_combo.grid(row=2, column=0, pady=(0, 18))

        btn = ctk.CTkButton(
            card,
            text="Aceptar",
            width=190,
            height=40,
            corner_radius=14,
            fg_color=colors["primary"],
            text_color=colors["dark"],
            hover_color=colors["hover_yellow"],
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.enter_control
        )
        btn.grid(row=3, column=0, pady=(0, 24))

    def enter_control(self):
        self.app.mostrar_control_dual()
