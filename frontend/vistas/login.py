"""Primera ventana: inicio de sesion del coordinador de repositorios."""
import tkinter as tk
from tkinter import messagebox, ttk

from backend.src.db.conexion import probar_conexion
from backend.src.repositorios import coordinadores

from .widgets import ejecutar_seguro


class VistaLogin(ttk.Frame):
    def __init__(self, master, al_ingresar):
        super().__init__(master, padding=30)
        self.al_ingresar = al_ingresar
        ttk.Label(self, text="Repositorios UCSM", font=("Helvetica", 20, "bold")).grid(
            row=0, column=0, columnspan=2, pady=(0, 4))
        ttk.Label(self, text="Ingreso del coordinador de repositorios").grid(
            row=1, column=0, columnspan=2, pady=(0, 18))

        ttk.Label(self, text="Correo institucional").grid(row=2, column=0, sticky="w", pady=4)
        self.correo = ttk.Entry(self, width=34)
        self.correo.grid(row=2, column=1, padx=(10, 0), pady=4)
        ttk.Label(self, text="Contraseña").grid(row=3, column=0, sticky="w", pady=4)
        self.clave = ttk.Entry(self, width=34, show="*")
        self.clave.grid(row=3, column=1, padx=(10, 0), pady=4)

        ttk.Button(self, text="Ingresar", command=self.ingresar).grid(
            row=4, column=0, columnspan=2, sticky="ew", pady=(16, 4))
        ttk.Button(self, text="Probar conexión con la base de datos",
                   command=self.probar).grid(row=5, column=0, columnspan=2, sticky="ew")

        self.correo.focus_set()
        self.bind_all("<Return>", lambda _e: self.ingresar() if self.winfo_exists() else None)

    def ingresar(self):
        ok, coordinador = ejecutar_seguro(self, coordinadores.autenticar,
                                          self.correo.get(), self.clave.get())
        if ok:
            self.unbind_all("<Return>")
            self.al_ingresar(coordinador)

    def probar(self):
        ok, info = ejecutar_seguro(self, probar_conexion)
        if ok:
            messagebox.showinfo(
                "Conexión exitosa",
                f"Servidor: {info['version']}\nBase: {info['base']}   Usuario: {info['usuario']}\n"
                f"Tablas: {info['tablas']} de 27   Índices: {info['indices']} de 21\n"
                f"Personas registradas: {info['filas_persona']}", parent=self)
