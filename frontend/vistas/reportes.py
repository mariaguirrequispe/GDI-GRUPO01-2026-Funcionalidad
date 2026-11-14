"""Pestana Reportes: las 15 consultas del aplicativo y la generacion de reportes."""
import tkinter as tk
from datetime import date
from tkinter import messagebox, ttk

from backend.src.repositorios import reportes

from .. import estilos
from .widgets import Encabezado, Tabla, ejecutar_seguro


class VistaReportes(ttk.Frame):
    def __init__(self, master, coordinador):
        super().__init__(master, padding=(10, 8))
        self.coordinador = coordinador
        self.catalogo = reportes.catalogo()
        Encabezado(self, "Reporte (Dashboard)",
                   "Consultas del repositorio y generación del reporte con sus indicadores.").pack(
            anchor="w", pady=(0, 8))
        cuaderno = ttk.Notebook(self)
        cuaderno.pack(fill="both", expand=True)
        self._armar_consultas(cuaderno)
        self._armar_generacion(cuaderno)

    # ---------- Consultas (reportes de solo lectura) ----------
    def _armar_consultas(self, cuaderno):
        marco = ttk.Frame(cuaderno, padding=8)
        cuaderno.add(marco, text=f"Consultas ({len(self.catalogo)})")
        barra = ttk.Frame(marco)
        barra.pack(fill="x")
        etiquetas = [f"{i:02d} · {titulo}" + ("   [JOIN]" if usa_join else "")
                     for i, titulo, usa_join in self.catalogo]
        self.combo = ttk.Combobox(barra, values=etiquetas, state="readonly", width=75)
        self.combo.current(0)
        self.combo.pack(side="left")
        self.combo.bind("<<ComboboxSelected>>", lambda _e: self.ejecutar())
        ttk.Button(barra, text="Ejecutar", style="Primario.TButton", command=self.ejecutar).pack(side="left", padx=8)
        self.estado = tk.StringVar()
        ttk.Label(marco, textvariable=self.estado).pack(anchor="w", pady=(6, 4))
        self.resultado = Tabla(marco, alto=18)
        self.resultado.pack(fill="both", expand=True)

    def ejecutar(self):
        id_consulta = self.catalogo[self.combo.current()][0]
        ok, resultado = ejecutar_seguro(self, reportes.ejecutar, id_consulta)
        if not ok:
            return
        titulo, columnas, filas = resultado
        self.resultado.configurar([(c, c, 150) for c in columnas])
        self.resultado.cargar(filas, con_id=False)
        self.estado.set(f"{titulo}: {len(filas)} fila(s)")

    # ---------- Generar reporte (sp_generar_reporte) ----------
    def _armar_generacion(self, cuaderno):
        marco = ttk.Frame(cuaderno, padding=8)
        cuaderno.add(marco, text="Generar reporte")
        barra = ttk.Frame(marco)
        barra.pack(fill="x")
        ttk.Label(barra, text="Fecha del reporte (AAAA-MM-DD):").pack(side="left")
        self.fecha = ttk.Entry(barra, width=14)
        self.fecha.insert(0, date.today().isoformat())
        self.fecha.pack(side="left", padx=6)
        ttk.Button(barra, text="Generar reporte", style="Primario.TButton", command=self.generar).pack(side="left")

        cuerpo = ttk.Frame(marco)
        cuerpo.pack(fill="both", expand=True, pady=(10, 0))
        cuerpo.columnconfigure(1, weight=1)
        cuerpo.rowconfigure(0, weight=1)
        self.emitidos = Tabla(cuerpo, [("fecha", "Reportes emitidos", 110),
                                       ("coordinador", "Coordinador", 230)], alto=18)
        self.emitidos.grid(row=0, column=0, sticky="ns", padx=(0, 10))
        self.emitidos.arbol.bind("<<TreeviewSelect>>", self._al_elegir_emitido)
        self.detalle = tk.Text(cuerpo, wrap="word", state="disabled", width=70)
        estilos.estilo_campo(self.detalle, texto=True)
        desplazamiento = ttk.Scrollbar(cuerpo, orient="vertical", command=self.detalle.yview)
        self.detalle.configure(yscrollcommand=desplazamiento.set)
        self.detalle.grid(row=0, column=1, sticky="nsew")
        desplazamiento.grid(row=0, column=2, sticky="ns")

    def refrescar(self):
        ok, filas = ejecutar_seguro(self, reportes.emitidos)
        if ok:
            self.emitidos.cargar(filas)

    def generar(self):
        fecha = self.fecha.get().strip()
        ok, _ = ejecutar_seguro(self, reportes.generar, fecha, self.coordinador["codigo_ucsm"])
        if ok:
            messagebox.showinfo("Reportes", f"Reporte del {fecha} generado.", parent=self)
            self.refrescar()
            self._mostrar(fecha)

    def _al_elegir_emitido(self, _evento=None):
        fecha = self.emitidos.seleccionada()
        if fecha:
            self._mostrar(fecha)

    def _mostrar(self, fecha):
        ok, texto = ejecutar_seguro(self, reportes.detalle, fecha)
        if ok:
            self.detalle.configure(state="normal")
            self.detalle.delete("1.0", "end")
            self.detalle.insert("1.0", texto)
            self.detalle.configure(state="disabled")
