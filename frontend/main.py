"""
Aplicativo de escritorio de Repositorios UCSM (Tkinter, sin frameworks).
Flujo: Login del coordinador -> ventana principal con Inicio, Investigadores,
Patentes, Historico y Reportes.
Uso (desde la raiz del repositorio):  python -m frontend.main
"""
import tkinter as tk
from .vistas.login import VistaLogin
from .vistas.principal import VistaPrincipal


class Aplicacion(tk.Tk):
    def __init__(self):
        super().__init__()
        self.geometry("1280x760")
        self.minsize(1050, 640)
        self.vista = None
        self.mostrar_login()

    def _cambiar(self, vista, centrada=False):
        if self.vista is not None:
            self.vista.destroy()
        self.vista = vista
        if centrada:
            vista.place(relx=0.5, rely=0.5, anchor="center")
        else:
            vista.pack(fill="both", expand=True)

    def mostrar_login(self):
        self.title("Repositorios UCSM - Ingreso")
        self._cambiar(VistaLogin(self, self.mostrar_principal), centrada=True)

    def mostrar_principal(self, coordinador):
        self.title("Repositorios UCSM")
        self._cambiar(VistaPrincipal(self, coordinador, self.mostrar_login))


if __name__ == "__main__":
    Aplicacion().mainloop()
