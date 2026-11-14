"""Pagina de inicio del coordinador: sus datos y el Dashboard (indicadores) del repositorio."""
import tkinter as tk
from datetime import date
from tkinter import messagebox, ttk

from backend.src.repositorios import coordinadores, reportes

from .. import estilos
from .widgets import Tarjeta, ejecutar_seguro

INDICADORES = (("investigadores", "Investigadores", estilos.AZUL_MEDIO),
               ("escuelas", "Escuelas profesionales", estilos.DORADO),
               ("publicaciones", "Publicaciones", estilos.AZUL_CLARO),
               ("patentes", "Patentes", estilos.AZUL_MEDIO),
               ("ods_vinculados", "ODS vinculados", estilos.DORADO))


class VistaInicio(ttk.Frame):
    def __init__(self, master, coordinador):
        super().__init__(master, padding=(14, 10))
        self.coordinador = coordinador
        self.columnconfigure(tuple(range(len(INDICADORES))), weight=1, uniform="ind")

        ttk.Label(self, text=f"Bienvenido(a), {coordinador['nombre']}", style="Titulo.TLabel").grid(
            row=0, column=0, columnspan=len(INDICADORES), sticky="w")
        ttk.Label(self, style="Suave.TLabel", text=(
            f"{coordinador['funcion']}  ·  {coordinador['direccion_adscrita']}  ·  "
            f"en el puesto desde {coordinador['fecha_ocupacion_puesto']}")).grid(
            row=1, column=0, columnspan=len(INDICADORES), sticky="w", pady=(0, 14))

        self.valores = {}
        for columna, (clave, titulo, color) in enumerate(INDICADORES):
            self.valores[clave] = self._tarjeta_indicador(columna, titulo, color)

        self.panel_ods = Tarjeta(self, "Ranking de ODS vinculados a los investigadores")
        self.panel_ods.grid(row=3, column=0, columnspan=3, sticky="nsew", padx=(0, 8), pady=(14, 0))
        self.panel_escuelas = Tarjeta(self, "Escuelas con más investigadores")
        self.panel_escuelas.grid(row=3, column=3, columnspan=2, sticky="nsew", padx=(8, 0), pady=(14, 0))

        acciones = Tarjeta(self, "Acciones rápidas")
        acciones.grid(row=4, column=0, columnspan=len(INDICADORES), sticky="ew", pady=(14, 0))
        fila = ttk.Frame(acciones.cuerpo, style="Tarjeta.TFrame")
        fila.pack(fill="x")
        ttk.Button(fila, text="Generar reporte de hoy", style="Primario.TButton",
                   command=self.generar_hoy).pack(side="left")
        self.estado = tk.StringVar()
        ttk.Label(fila, textvariable=self.estado, style="TarjetaSuave.TLabel").pack(side="left", padx=14)
        self.rowconfigure(3, weight=1)

    def _tarjeta_indicador(self, columna, titulo, color):
        tarjeta = tk.Frame(self, background=estilos.TARJETA, highlightthickness=1,
                           highlightbackground=estilos.BORDE, borderwidth=0)
        tarjeta.grid(row=2, column=columna, sticky="nsew", padx=5)
        tk.Frame(tarjeta, background=color, height=5).pack(fill="x")
        variable = tk.StringVar(value="-")
        tk.Label(tarjeta, textvariable=variable, background=estilos.TARJETA, foreground=estilos.AZUL,
                 font=estilos.fuente(28, True)).pack(pady=(10, 0))
        tk.Label(tarjeta, text=titulo, background=estilos.TARJETA, foreground=estilos.TEXTO_SUAVE,
                 font=estilos.fuente(10)).pack(pady=(0, 12))
        return variable

    def refrescar(self):
        ok, datos = ejecutar_seguro(self, reportes.indicadores)
        if ok:
            for clave, variable in self.valores.items():
                variable.set(str(datos[clave]))
            self._lista_ods(datos["ranking_ods"])
            self._lista_escuelas(datos["top_escuelas"])
        ok, resumen = ejecutar_seguro(self, coordinadores.resumen, self.coordinador["codigo_ucsm"])
        if ok:
            self.estado.set(f"Reportes emitidos: {resumen['reportes']}  ·  por usted: {resumen['mis_reportes']}")

    @staticmethod
    def _vaciar(tarjeta):
        for hijo in tarjeta.cuerpo.winfo_children()[1:]:     # conserva la etiqueta del titulo
            hijo.destroy()

    def _lista_ods(self, ranking):
        self._vaciar(self.panel_ods)
        if not ranking:
            ttk.Label(self.panel_ods.cuerpo, text="Aún no hay ODS registrados.",
                      style="TarjetaSuave.TLabel").pack(anchor="w")
            return
        maximo = max(total for _ods, total in ranking)
        for ods, total in ranking:
            fila = ttk.Frame(self.panel_ods.cuerpo, style="Tarjeta.TFrame")
            fila.pack(fill="x", pady=3)
            ttk.Label(fila, text=ods, style="Tarjeta.TLabel", width=46).pack(side="left")
            ttk.Progressbar(fila, style="Barra.Horizontal.TProgressbar", maximum=maximo, value=total,
                            length=140).pack(side="left", padx=8)
            ttk.Label(fila, text=str(total), style="TarjetaTitulo.TLabel").pack(side="left")

    def _lista_escuelas(self, top):
        self._vaciar(self.panel_escuelas)
        if not top:
            ttk.Label(self.panel_escuelas.cuerpo, text="Aún no hay investigadores registrados.",
                      style="TarjetaSuave.TLabel").pack(anchor="w")
            return
        for puesto, (escuela, total) in enumerate(top, start=1):
            fila = ttk.Frame(self.panel_escuelas.cuerpo, style="Tarjeta.TFrame")
            fila.pack(fill="x", pady=4)
            ttk.Label(fila, text=f"{puesto}.", style="TarjetaTitulo.TLabel", width=3).pack(side="left")
            ttk.Label(fila, text=escuela, style="Tarjeta.TLabel").pack(side="left")
            ttk.Label(fila, text=f"{total} inv.", style="TarjetaSuave.TLabel").pack(side="right")

    def generar_hoy(self):
        hoy = date.today()
        ok, _ = ejecutar_seguro(self, reportes.generar, hoy, self.coordinador["codigo_ucsm"])
        if ok:
            messagebox.showinfo("Reporte generado", f"Se generó el reporte del {hoy.isoformat()}.\n"
                                "Puede verlo en la pestaña Reportes.", parent=self)
            self.refrescar()
