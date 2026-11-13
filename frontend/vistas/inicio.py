"""Pagina de inicio del coordinador: sus datos, conteos generales y acceso rapido al reporte."""
import tkinter as tk
from datetime import date
from tkinter import messagebox, ttk

from backend.src.repositorios import coordinadores, reportes

from .widgets import ejecutar_seguro

TARJETAS = (("investigadores", "Investigadores"), ("patentes", "Patentes"),
            ("publicaciones", "Publicaciones"), ("reportes", "Reportes emitidos"),
            ("mis_reportes", "Emitidos por mí"))


class VistaInicio(ttk.Frame):
    def __init__(self, master, coordinador):
        super().__init__(master, padding=16)
        self.coordinador = coordinador
        ttk.Label(self, text=f"Bienvenido(a), {coordinador['nombre']}",
                  font=("Helvetica", 16, "bold")).grid(row=0, column=0, columnspan=5, sticky="w")
        detalle = (f"{coordinador['funcion']}  ·  {coordinador['direccion_adscrita']}\n"
                   f"Correo: {coordinador['correo_electronico']}   "
                   f"Código UCSM: {coordinador['codigo_ucsm']}   "
                   f"En el puesto desde: {coordinador['fecha_ocupacion_puesto']}")
        ttk.Label(self, text=detalle, justify="left").grid(
            row=1, column=0, columnspan=5, sticky="w", pady=(4, 16))

        self.contadores = {}
        for columna, (clave, titulo) in enumerate(TARJETAS):
            tarjeta = ttk.LabelFrame(self, text=titulo, padding=(18, 10))
            tarjeta.grid(row=2, column=columna, padx=6, sticky="nsew")
            variable = tk.StringVar(value="-")
            ttk.Label(tarjeta, textvariable=variable, font=("Helvetica", 22, "bold")).pack()
            self.contadores[clave] = variable

        acciones = ttk.LabelFrame(self, text="Acciones rápidas", padding=12)
        acciones.grid(row=3, column=0, columnspan=5, sticky="ew", pady=(20, 0))
        ttk.Button(acciones, text="Generar reporte de hoy", command=self.generar_hoy).pack(side="left")
        ttk.Label(acciones, text="  Guarda las estadísticas de hoy (sp_generar_reporte). "
                                 "Use las pestañas para gestionar investigadores, patentes y publicaciones."
                  ).pack(side="left")

    def refrescar(self):
        ok, datos = ejecutar_seguro(self, coordinadores.resumen, self.coordinador["codigo_ucsm"])
        if ok:
            for clave, variable in self.contadores.items():
                variable.set(str(datos[clave]))

    def generar_hoy(self):
        hoy = date.today()
        ok, _ = ejecutar_seguro(self, reportes.generar, hoy, self.coordinador["codigo_ucsm"])
        if ok:
            messagebox.showinfo("Reporte generado", f"Se generó el reporte del {hoy.isoformat()}.\n"
                                "Puede verlo en la pestaña Reportes.", parent=self)
            self.refrescar()
