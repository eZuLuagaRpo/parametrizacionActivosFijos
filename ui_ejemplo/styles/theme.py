
import customtkinter as ctk


def apply_theme():
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")

    return {
        # Paleta primaria Bancolombia
        "white": "#FFFFFF",
        "dark": "#2c2a29",

        # Paleta secundaria Bancolombia
        "yellow": "#fdda24",
        "green": "#00c389",
        "purple": "#9063cd",
        "orange": "#ff7f41",
        "pink": "#f5b6cd",
        "blue": "#59cbe8",

        # Alias usados por tus vistas actuales
        "primary": "#fdda24",
        "secondary": "#2c2a29",
        "card": "#FFFFFF",

        # Apoyos UI
        "background": "#F7F7F7",
        "border": "#E4E1DD",
        "muted": "#706C68",
        "input": "#FFFFFF",
        "input_border": "#D8D4CF",
        "hover_yellow": "#E6C800",
        "hover_dark": "#1F1D1C",
        "disabled": "#B8B4AF",
        "danger": "#D93025"
    }
