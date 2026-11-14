"""
Aplicativo de escritorio de Repositorios UCSM (Tkinter, sin frameworks).
Flujo: Login del coordinador -> ventana principal con Inicio, Investigadores,
Patentes, Historico y Reportes.
Uso (desde la raiz del repositorio):  python -m frontend.main
"""
import tkinter as tk

from . import estilos
from .vistas.login import VistaLogin
from .vistas.principal import VistaPrincipal


class Aplicacion(tk.Tk):
    def __init__(self):
        super().__init__()
        self.geometry("1320x800")
        self.minsize(1100, 680)
        estilos.aplicar(self)
        self.vista = None
        self.mostrar_login()

    def _cambiar(self, vista):
        if self.vista is not None:
            self.vista.destroy()
        self.vista = vista
        vista.pack(fill="both", expand=True)

    def mostrar_login(self):
        self.title("Repositorios UCSM - Ingreso")
        self._cambiar(VistaLogin(self, self.mostrar_principal))

    def mostrar_principal(self, coordinador):
        self.title("Repositorios UCSM")
        self._cambiar(VistaPrincipal(self, coordinador, self.mostrar_login))


if __name__ == "__main__":
    Aplicacion().mainloop()
