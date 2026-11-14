"""Primera ventana: inicio de sesion del coordinador de repositorios."""
import tkinter as tk
from tkinter import messagebox, ttk

from backend.src.db.conexion import probar_conexion
from backend.src.repositorios import coordinadores

from .. import estilos
from .widgets import Tarjeta, ejecutar_seguro


class VistaLogin(ttk.Frame):
    def __init__(self, master, al_ingresar):
        super().__init__(master)
        self.al_ingresar = al_ingresar
        self.columnconfigure(0, weight=2, uniform="login")
        self.columnconfigure(1, weight=3, uniform="login")
        self.rowconfigure(0, weight=1)
        self._panel_institucional()
        self._formulario()
        self.correo.focus_set()
        self.bind_all("<Return>", lambda _e: self.ingresar())

    def _panel_institucional(self):
        panel = tk.Frame(self, background=estilos.AZUL)
        panel.grid(row=0, column=0, sticky="nsew")
        centro = tk.Frame(panel, background=estilos.AZUL)
        centro.place(relx=0.5, rely=0.5, anchor="center")
        tk.Label(centro, text="UCSM", background=estilos.AZUL, foreground=estilos.DORADO,
                 font=estilos.fuente(38, True)).pack()
        tk.Label(centro, text="Repositorios de Investigación", background=estilos.AZUL,
                 foreground="white", font=estilos.fuente(17, True)).pack(pady=(2, 14))
        tk.Frame(centro, background=estilos.DORADO, height=3, width=70).pack(pady=(0, 16))
        tk.Label(centro, text="Registro de investigadores y seguimiento del uso de "
                              "repositorios de investigación", background=estilos.AZUL,
                 foreground=estilos.TEXTO_CLARO, font=estilos.fuente(11), wraplength=300,
                 justify="center").pack()
        tk.Label(panel, text="Vicerrectorado de Investigación · Universidad Católica de Santa María",
                 background=estilos.AZUL, foreground=estilos.TEXTO_CLARO, font=estilos.fuente(9),
                 wraplength=320, justify="center").place(relx=0.5, rely=0.94, anchor="s")

    def _formulario(self):
        lado = tk.Frame(self, background=estilos.FONDO)
        lado.grid(row=0, column=1, sticky="nsew")
        tarjeta = Tarjeta(lado, padding=34)
        tarjeta.place(relx=0.5, rely=0.5, anchor="center")
        c = tarjeta.cuerpo
        ttk.Label(c, text="Iniciar sesión", style="TarjetaTitulo.TLabel",
                  font=estilos.fuente(18, True)).grid(row=0, column=0, sticky="w")
        ttk.Label(c, text="Ingrese con su correo institucional", style="TarjetaSuave.TLabel").grid(
            row=1, column=0, sticky="w", pady=(0, 18))
        ttk.Label(c, text="Correo institucional", style="Tarjeta.TLabel").grid(row=2, column=0, sticky="w")
        self.correo = ttk.Entry(c, width=36)
        self.correo.grid(row=3, column=0, sticky="ew", pady=(2, 12))
        ttk.Label(c, text="Contraseña", style="Tarjeta.TLabel").grid(row=4, column=0, sticky="w")
        self.clave = ttk.Entry(c, width=36, show="•")
        self.clave.grid(row=5, column=0, sticky="ew", pady=(2, 18))
        ttk.Button(c, text="Ingresar", style="Primario.TButton", command=self.ingresar).grid(
            row=6, column=0, sticky="ew")
        ttk.Button(c, text="Probar conexión con la base de datos", command=self.probar).grid(
            row=7, column=0, sticky="ew", pady=(10, 0))

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
