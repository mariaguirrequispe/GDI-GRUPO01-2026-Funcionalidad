"""Ventana principal del coordinador: barra superior y pestanas de cada modulo."""
from tkinter import ttk

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
        barra = ttk.Frame(self, padding=(10, 6))
        barra.pack(fill="x")
        ttk.Label(barra, text=f"Coordinador: {coordinador['nombre']}  ·  {coordinador['funcion']}",
                  font=("Helvetica", 10, "bold")).pack(side="left")
        ttk.Button(barra, text="Cerrar sesión", command=al_salir).pack(side="right")

        self.cuaderno = ttk.Notebook(self)
        self.cuaderno.pack(fill="both", expand=True, padx=6, pady=(0, 6))
        for titulo, clase in PESTANAS:
            self.cuaderno.add(clase(self.cuaderno, coordinador), text=titulo)
        self.cuaderno.bind("<<NotebookTabChanged>>", self._al_cambiar)
        self.after_idle(self._al_cambiar)

    def _al_cambiar(self, _evento=None):
        """Cada pestana vuelve a leer la base al mostrarse, para no enseñar datos viejos."""
        vista = self.nametowidget(self.cuaderno.select())
        if hasattr(vista, "refrescar"):
            vista.refrescar()
