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
        self._ajustar_a_la_pantalla()
        estilos.aplicar(self)
        self.vista = None
        self.mostrar_login()

    def _ajustar_a_la_pantalla(self):
        """Tamano inicial segun la pantalla (en una de 1366x768 una ventana fija se cortaria)."""
        ancho_pantalla, alto_pantalla = self.winfo_screenwidth(), self.winfo_screenheight()
        ancho = min(1320, ancho_pantalla - 60)
        alto = min(800, alto_pantalla - 110)
        x = max(0, (ancho_pantalla - ancho) // 2)
        y = max(0, (alto_pantalla - alto) // 2 - 20)
        self.geometry(f"{ancho}x{alto}+{x}+{y}")
        self.minsize(min(980, ancho), min(560, alto))

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
