"""Ventana principal del coordinador: cabecera institucional y pestanas de cada modulo."""
import tkinter as tk
from tkinter import ttk

from .. import estilos
from .historico import VistaHistorico
from .inicio import VistaInicio
from .investigadores import VistaInvestigadores
from .patentes import VistaPatentes
from .reportes import VistaReportes

PESTANAS = (("Inicio", VistaInicio), ("Investigadores", VistaInvestigadores),
            ("Patentes", VistaPatentes), ("Histórico", VistaHistorico),
            ("Reportes", VistaReportes))


class VistaPrincipal(ttk.Frame):
    def __init__(self, master, coordinador, al_salir):
        super().__init__(master)
        self._cabecera(coordinador, al_salir)
        self.cuaderno = ttk.Notebook(self)
        self.cuaderno.pack(fill="both", expand=True, padx=12, pady=(6, 12))
        for titulo, clase in PESTANAS:
            self.cuaderno.add(clase(self.cuaderno, coordinador), text=titulo)
        self.cuaderno.bind("<<NotebookTabChanged>>", self._al_cambiar)
        self.after_idle(self._al_cambiar)

    def _cabecera(self, coordinador, al_salir):
        barra = tk.Frame(self, background=estilos.AZUL)
        barra.pack(fill="x")
        interior = tk.Frame(barra, background=estilos.AZUL)
        interior.pack(fill="x", padx=20, pady=12)
        izquierda = tk.Frame(interior, background=estilos.AZUL)
        izquierda.pack(side="left")
        tk.Label(izquierda, text="Repositorios UCSM", background=estilos.AZUL, foreground="white",
                 font=estilos.fuente(17, True)).pack(anchor="w")
        tk.Label(izquierda, text="Registro de investigadores y seguimiento de repositorios de investigación",
                 background=estilos.AZUL, foreground=estilos.TEXTO_CLARO,
                 font=estilos.fuente(9)).pack(anchor="w")
        ttk.Button(interior, text="Cerrar sesión", style="Dorado.TButton", command=al_salir).pack(
            side="right", padx=(18, 0))
        derecha = tk.Frame(interior, background=estilos.AZUL)
        derecha.pack(side="right")
        tk.Label(derecha, text=coordinador["nombre"], background=estilos.AZUL, foreground="white",
                 font=estilos.fuente(11, True)).pack(anchor="e")
        tk.Label(derecha, text=coordinador["funcion"], background=estilos.AZUL,
                 foreground=estilos.DORADO, font=estilos.fuente(9, True)).pack(anchor="e")
        tk.Frame(self, background=estilos.DORADO, height=3).pack(fill="x")

    def _al_cambiar(self, _evento=None):
        """Cada pestana vuelve a leer la base al mostrarse, para no enseñar datos viejos."""
        vista = self.nametowidget(self.cuaderno.select())
        if hasattr(vista, "refrescar"):
            vista.refrescar()
