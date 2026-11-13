"""Pestana Patentes: listado + formulario para registrar, modificar y eliminar."""
import tkinter as tk
from tkinter import messagebox, ttk

from backend.src.repositorios import investigadores, patentes

from .widgets import Formulario, Tabla, ejecutar_seguro

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
        super().__init__(master, padding=8)
        self.coordinador = coordinador
        self.editando = None                    # numero de patente en edicion
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.tabla = Tabla(self, [("n", "N.º patente", 100), ("titulo", "Título", 280),
                                  ("fecha", "Registro", 90), ("pais", "País", 70),
                                  ("inventores", "Inventores", 220)], alto=20)
        self.tabla.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        self.tabla.arbol.bind("<<TreeviewSelect>>", self._al_seleccionar)

        derecha = ttk.Frame(self, padding=8, relief="groove", borderwidth=2)
        derecha.grid(row=0, column=1, sticky="ns")
        self.titulo = tk.StringVar()
        ttk.Label(derecha, textvariable=self.titulo, font=("Helvetica", 11, "bold")).pack(
            anchor="w", pady=(0, 8))
        self.form = Formulario(derecha, CAMPOS)
        self.form.pack()
        botones = ttk.Frame(derecha)
        botones.pack(pady=(10, 0))
        ttk.Button(botones, text="Nueva", command=self.nueva).pack(side="left", padx=4)
        ttk.Button(botones, text="Guardar", command=self.guardar).pack(side="left", padx=4)
        ttk.Button(botones, text="Eliminar", command=self.eliminar).pack(side="left", padx=4)
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
        self.titulo.set(" Nueva patente ")

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
            self.titulo.set(f" Editando patente {numero} ")

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