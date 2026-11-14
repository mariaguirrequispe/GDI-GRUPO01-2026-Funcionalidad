"""Pestana Patentes: listado + formulario para registrar, modificar y eliminar."""
import tkinter as tk
from tkinter import messagebox, ttk

from backend.src.repositorios import investigadores, patentes

from .widgets import Encabezado, Formulario, Tabla, Tarjeta, ejecutar_seguro

CAMPOS = [
    ("n_patente", "Número de patente (PE-123456)", "entry", None),
    ("titulo", "Título", "entry", None),
    ("editorial", "Editorial", "entry", None),
    ("fecha_registro", "Fecha de registro (AAAA-MM-DD)", "entry", None),
    ("cip", "CIP", "entry", None),
    ("pais", "País", "entry", None),
    ("inventores", "Inventores (selección múltiple)", "lista", []),
    ("ocde", "Clasificación OCDE\n(una línea: campo | objetivo)", "texto", 4),
]


class VistaPatentes(ttk.Frame):
    def __init__(self, master, coordinador):
        super().__init__(master, padding=(10, 8))
        self.coordinador = coordinador
        self.editando = None                    # numero de patente en edicion
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        Encabezado(self, "Formato de registro de patente",
                   "Cada patente debe tener al menos un inventor registrado como investigador.").grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 8))

        self.tabla = Tabla(self, [("n", "N.º patente", 100), ("titulo", "Título", 280),
                                  ("fecha", "Registro", 90), ("pais", "País", 70),
                                  ("inventores", "Inventores", 220)], alto=20)
        self.tabla.grid(row=1, column=0, sticky="nsew", padx=(0, 12))
        self.tabla.arbol.bind("<<TreeviewSelect>>", self._al_seleccionar)

        self.panel = Tarjeta(self, "")
        self.panel.grid(row=1, column=1, sticky="ns")
        self.form = Formulario(self.panel.cuerpo, CAMPOS)
        self.form.pack()
        botones = ttk.Frame(self.panel.cuerpo, style="Tarjeta.TFrame")
        botones.pack(fill="x", pady=(12, 0))
        ttk.Button(botones, text="Nueva", command=self.nueva).pack(side="left")
        ttk.Button(botones, text="Eliminar", style="Peligro.TButton", command=self.eliminar).pack(side="right")
        ttk.Button(botones, text="Guardar", style="Primario.TButton", command=self.guardar).pack(
            side="right", padx=8)
        self.nueva()

    def refrescar(self):
        ok, filas = ejecutar_seguro(self, patentes.listar)
        if ok:
            self.tabla.cargar(filas)
        ok, opciones = ejecutar_seguro(self, investigadores.opciones)
        if ok:
            self.form.establecer_opciones("inventores", opciones)

    def nueva(self):
        self.editando = None
        self.form.bloquear(("n_patente",), False)
        self.form.limpiar()
        self.tabla.deseleccionar()
        self.panel.titulo.set("Nueva patente")

    def _al_seleccionar(self, _evento=None):
        numero = self.tabla.seleccionada()
        if not numero:
            return
        ok, datos = ejecutar_seguro(self, patentes.obtener, numero)
        if ok and datos:
            self.form.bloquear(("n_patente",), False)
            self.form.poner(datos)
            self.form.bloquear(("n_patente",), True)
            self.editando = numero
            self.panel.titulo.set(f"Editando patente {numero}")

    def guardar(self):
        datos = self.form.valores()
        if self.editando is None:
            ok, _ = ejecutar_seguro(self, patentes.registrar, datos, self.coordinador["codigo_ucsm"])
            mensaje = "Patente registrada correctamente."
        else:
            ok, _ = ejecutar_seguro(self, patentes.modificar, self.editando, datos)
            mensaje = "Patente modificada correctamente."
        if ok:
            messagebox.showinfo("Patentes", mensaje, parent=self)
            self.nueva()
            self.refrescar()

    def eliminar(self):
        if self.editando is None:
            messagebox.showwarning("Patentes", "Seleccione una patente de la lista.", parent=self)
            return
        if not messagebox.askyesno("Eliminar", f"¿Eliminar la patente {self.editando}?\n"
                                   "Se borrarán también sus inventores y clasificación OCDE.",
                                   parent=self):
            return
        ok, _ = ejecutar_seguro(self, patentes.eliminar, self.editando)
        if ok:
            messagebox.showinfo("Patentes", "Patente eliminada.", parent=self)
            self.nueva()
            self.refrescar()
