"""
Ventana inicial del aplicativo (Tkinter, libreria estandar de Python).
Muestra el formulario de conexion y el boton "Probar conexion".
Uso:  python -m fronted.main
"""
import tkinter as tk
from tkinter import messagebox, ttk

from backend.src.db.conexion import ErrorConexion, leer_configuracion, probar_conexion


class VentanaConexion(tk.Tk):
    CAMPOS = (("Servidor", "host"), ("Puerto", "port"), ("Base de datos", "dbname"),
              ("Usuario", "user"), ("Contrasenia", "password"))

    def __init__(self):
        super().__init__()
        self.title("Repositorios UCSM - Conexion a la base de datos")
        self.resizable(False, False)
        self.entradas = {}
        marco = ttk.Frame(self, padding=14)
        marco.grid()
        for fila, (etiqueta, clave) in enumerate(self.CAMPOS):
            ttk.Label(marco, text=etiqueta).grid(row=fila, column=0, sticky="w", pady=3)
            e = ttk.Entry(marco, width=32, show="*" if clave == "password" else "")
            e.grid(row=fila, column=1, pady=3, padx=(8, 0))
            self.entradas[clave] = e
        ttk.Button(marco, text="Probar conexion", command=self.probar).grid(
            row=len(self.CAMPOS), column=0, columnspan=2, pady=10)
        self.estado = tk.Text(marco, width=52, height=9, state="disabled")
        self.estado.grid(row=len(self.CAMPOS) + 1, column=0, columnspan=2)
        self.cargar_config()

    def cargar_config(self):
        try:
            cfg = leer_configuracion()
        except ErrorConexion as e:
            self.escribir(str(e))
            return
        for clave, entrada in self.entradas.items():
            entrada.insert(0, cfg.get(clave, ""))

    def escribir(self, texto):
        self.estado.configure(state="normal")
        self.estado.delete("1.0", "end")
        self.estado.insert("end", texto)
        self.estado.configure(state="disabled")

    def probar(self):
        cfg = {k: e.get().strip() for k, e in self.entradas.items()}
        cfg["connect_timeout"] = "5"
        try:
            info = probar_conexion(cfg)
        except ErrorConexion as e:
            self.escribir("CONEXION FALLIDA\n" + str(e))
            messagebox.showerror("Conexion", str(e))
            return
        self.escribir(
            "CONEXION EXITOSA\n"
            f"Servidor: {info['version']}\n"
            f"Base: {info['base']}   Usuario: {info['usuario']}\n"
            f"Tablas: {info['tablas']} de 27   Indices: {info['indices']} de 21\n"
            f"Personas registradas: {info['filas_persona']}")


if __name__ == "__main__":
    VentanaConexion().mainloop()
