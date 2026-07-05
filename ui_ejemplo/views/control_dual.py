import customtkinter as ctk
from tkinter import filedialog
from utils.control_dual_robot import ejecutar_control_dual
import os
from utils.query_ejecucion import _test_lz_conexion, _test_nacional_conexion
from datetime import datetime
from tkcalendar import DateEntry
import tkinter as tk

class ControlDualVista(ctk.CTkFrame):
    def __init__(self, master, colors, app):
        super().__init__(
            master,
            fg_color="transparent",
            width=430,
            height=650
        )

        self.colors = colors
        self.app = app
        self.excel_paths = []
        self.conexion_ok = False
        self.fecha_seleccionada = None

        self.pack_propagate(False)
        self.grid_propagate(False)

        card = ctk.CTkFrame(
            self,
            width=430,
            height=620,
            fg_color=colors["card"],
            corner_radius=24,
            border_width=1,
            border_color=colors["border"]
        )
        card.place(x=0, y=0)
        card.pack_propagate(False)
        card.grid_propagate(False)

        ctk.CTkLabel(
            card,
            text="Control Dual",
            font=ctk.CTkFont(size=25, weight="bold"),
            text_color=colors["secondary"]
        ).pack(pady=(0, 14))

        ctk.CTkFrame(
            card,
            height=3,
            width=72,
            fg_color=colors["yellow"],
            corner_radius=10
        ).pack(pady=(0, 14))

        ctk.CTkLabel(
            card,
            text="Credenciales LZ",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=colors["secondary"]
        ).pack(pady=(2, 5))

        self.lz_user = ctk.CTkEntry(
            card,
            placeholder_text="Usuario LZ",
            width=275,
            height=36,
            corner_radius=12,
            fg_color=colors["input"],
            border_color=colors["input_border"],
            text_color=colors["dark"],
            placeholder_text_color=colors["muted"]
        )
        self.lz_user.pack(pady=5)

        self.lz_pass = ctk.CTkEntry(
            card,
            placeholder_text="Password LZ",
            show="*",
            width=275,
            height=36,
            corner_radius=12,
            fg_color=colors["input"],
            border_color=colors["input_border"],
            text_color=colors["dark"],
            placeholder_text_color=colors["muted"]
        )
        self.lz_pass.pack(pady=5)

        ctk.CTkLabel(
            card,
            text="Credenciales Nacional",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=colors["secondary"]
        ).pack(pady=(13, 5))

        self.nac_user = ctk.CTkEntry(
            card,
            placeholder_text="Usuario Nacional",
            width=275,
            height=36,
            corner_radius=12,
            fg_color=colors["input"],
            border_color=colors["input_border"],
            text_color=colors["dark"],
            placeholder_text_color=colors["muted"]
        )
        self.nac_user.pack(pady=5)

        self.nac_pass = ctk.CTkEntry(
            card,
            placeholder_text="Password Nacional",
            show="*",
            width=275,
            height=36,
            corner_radius=12,
            fg_color=colors["input"],
            border_color=colors["input_border"],
            text_color=colors["dark"],
            placeholder_text_color=colors["muted"]
        )
        self.nac_pass.pack(pady=5)

        self.excel_label = ctk.CTkLabel(
            card,
            text="Ningún archivo seleccionado",
            text_color=colors["muted"],
            font=ctk.CTkFont(size=12)
        )
        self.excel_label.pack(pady=(15, 6))

        ctk.CTkButton(
            card,
            text="Seleccionar Excel",
            width=225,
            height=38,
            corner_radius=14,
            fg_color=colors["dark"],
            text_color=colors["white"],
            hover_color=colors["hover_dark"],
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self.select_excel
        ).pack(pady=7)
        
        self.fecha_label = ctk.CTkLabel(
    card,
    text="Fecha no seleccionada, se usará la fecha actual",
    text_color=colors["muted"],
    font=ctk.CTkFont(size=12)
)
        self.fecha_label.pack(pady=(5, 3))

        ctk.CTkButton(
            card,
            text="Escoger fecha",
            width=225,
            height=38,
            corner_radius=14,
            fg_color=colors["dark"],
            text_color=colors["white"],
            hover_color=colors["hover_dark"],
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self.abrir_selector_fecha
        ).pack(pady=7)
        
        ctk.CTkButton(
            card,
            text="Probar conexión",
            width=225,
            height=38,
            corner_radius=14,
            fg_color=colors["dark"],
            text_color=colors["white"],
            hover_color=colors["hover_dark"],
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self.probar_conexion
        ).pack(pady=7)

        self.run_btn = ctk.CTkButton(
            card,
            text="Ejecutar Robot",
            width=225,
            height=40,
            corner_radius=14,
            fg_color=colors["primary"],
            text_color=colors["dark"],
            hover_color=colors["hover_yellow"],
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self.run_robot,
            state="disabled"
        )
        self.run_btn.pack(pady=(14, 7))

        ctk.CTkButton(
            card,
            text="Volver al inicio",
            width=225,
            height=36,
            corner_radius=14,
            fg_color=colors["white"],
            text_color=colors["dark"],
            border_width=1,
            border_color=colors["dark"],
            hover_color=colors["border"],
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self.app.mostrar_menu
        ).pack(pady=(0, 18))

        self.lz_user.bind("<KeyRelease>", lambda e: self.validar_formulario())
        self.lz_pass.bind("<KeyRelease>", lambda e: self.validar_formulario())
        self.nac_user.bind("<KeyRelease>", lambda e: self.validar_formulario())
        self.nac_pass.bind("<KeyRelease>", lambda e: self.validar_formulario())

    def credenciales_cambiaron(self):
        self.conexion_ok = False
        self.validar_formulario()
    
    def select_excel(self):
        paths = filedialog.askopenfilenames(
            filetypes=[("Archivos Excel", "*.xlsx *.xls *.xlsm")]
        )

        if paths:
            self.excel_paths = list(paths)

            if len(self.excel_paths) == 1:
                texto = os.path.basename(self.excel_paths[0])
            else:
                texto = f"{len(self.excel_paths)} archivo(s) seleccionado(s)"

            self.excel_label.configure(text=texto, text_color=self.colors["muted"])
            self.validar_formulario()

    def validar_formulario(self):
        lz_user = self.lz_user.get().strip()
        lz_pass = self.lz_pass.get().strip()
        nac_user = self.nac_user.get().strip()
        nac_pass = self.nac_pass.get().strip()

        credenciales_ok = all([lz_user, lz_pass, nac_user, nac_pass])
        excel_ok = len(self.excel_paths) > 0

        if credenciales_ok and excel_ok and self.conexion_ok:
            self.run_btn.configure(state="normal")
        else:
            self.run_btn.configure(state="disabled")
            
    def probar_conexion(self):
        lz_user = self.lz_user.get().strip()
        lz_pass = self.lz_pass.get().strip()
        nac_user = self.nac_user.get().strip()
        nac_pass = self.nac_pass.get().strip()

        if not all([lz_user, lz_pass, nac_user, nac_pass]):
            self.excel_label.configure(
                text="Complete todas las credenciales antes de probar conexión",
                text_color=self.colors["danger"]
            )
            self.conexion_ok = False
            self.validar_formulario()
            return

        self.excel_label.configure(
            text="Probando conexión...",
            text_color=self.colors["muted"]
        )

        lz_ok = _test_lz_conexion(lz_user, lz_pass)
        nacional_ok = _test_nacional_conexion(nac_user, nac_pass)

        if lz_ok and nacional_ok:
            self.conexion_ok = True
            self.excel_label.configure(
                text="Conexión exitosa",
                text_color=self.colors["secondary"]
            )
        else:
            self.conexion_ok = False

            if not lz_ok and not nacional_ok:
                mensaje = "Error en conexión LZ y Nacional"
            elif not lz_ok:
                mensaje = "Error en conexión LZ"
            else:
                mensaje = "Error en conexión Nacional"

            self.excel_label.configure(
                text=mensaje,
                text_color=self.colors["danger"]
            )

        self.validar_formulario()
        
        
    def abrir_selector_fecha(self):
        ventana = ctk.CTkToplevel(self)
        ventana.title("Escoger fecha")
        ventana.geometry("300x220")
        ventana.resizable(False, False)
        ventana.grab_set()

        ctk.CTkLabel(
            ventana,
            text="Seleccione la fecha",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(18, 10))

        calendario = DateEntry(
            ventana,
            date_pattern="dd.mm.yyyy",
            width=18
        )
        calendario.pack(pady=10)

        def confirmar_fecha():
            self.fecha_seleccionada = calendario.get_date().strftime("%d.%m.%Y")
            self.fecha_label.configure(
                text=f"Fecha seleccionada: {self.fecha_seleccionada}",
                text_color=self.colors["secondary"]
            )
            ventana.destroy()

        def limpiar_fecha():
            self.fecha_seleccionada = None
            self.fecha_label.configure(
                text="Fecha no seleccionada, se usará la fecha actual",
                text_color=self.colors["muted"]
            )
            ventana.destroy()

        ctk.CTkButton(
            ventana,
            text="Aceptar",
            width=160,
            command=confirmar_fecha
        ).pack(pady=(10, 5))

        ctk.CTkButton(
            ventana,
            text="Usar fecha actual",
            width=160,
            fg_color=self.colors["white"],
            text_color=self.colors["dark"],
            border_width=1,
            border_color=self.colors["dark"],
            command=limpiar_fecha
        ).pack(pady=5)

    def run_robot(self):
        if not self.excel_paths:
            self.excel_label.configure(
                text="Seleccione un archivo Excel",
                text_color=self.colors["danger"]
            )
            self.run_btn.configure(state="disabled")
            return

        lz_user = self.lz_user.get().strip()
        lz_pass = self.lz_pass.get().strip()
        nac_user = self.nac_user.get().strip()
        nac_pass = self.nac_pass.get().strip()

        if not all([lz_user, lz_pass, nac_user, nac_pass]):
            self.excel_label.configure(
                text="Complete todas las credenciales",
                text_color=self.colors["danger"]
            )
            self.run_btn.configure(state="disabled")
            return

        if not self.conexion_ok:
            self.excel_label.configure(
                text="Primero debe probar la conexión",
                text_color=self.colors["danger"]
            )
            self.run_btn.configure(state="disabled")
            return
    
        fecha_proceso = self.fecha_seleccionada or datetime.now().strftime("%d.%m.%Y")

        ejecutar_control_dual(
            self.excel_paths,
            lz_user,
            lz_pass,
            nac_user,
            nac_pass,
            fecha_proceso
        )
