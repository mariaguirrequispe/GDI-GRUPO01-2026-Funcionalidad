"""Pestana Investigadores: listado + formulario para registrar, modificar y eliminar."""
import tkinter as tk
from tkinter import messagebox, ttk

from backend.src.repositorios import investigadores
from backend.src.repositorios.catalogos import GENEROS, ODS

from .widgets import Formulario, Tabla, ejecutar_seguro

CAMPOS = [
    ("dni", "DNI", "entry", None),
    ("nombres", "Nombres", "entry", None),
    ("apellido_paterno", "Apellido paterno", "entry", None),
    ("apellido_materno", "Apellido materno", "entry", None),
    ("genero", "Género", "combo", GENEROS),
    ("fecha_nacimiento", "Fecha de nacimiento (AAAA-MM-DD)", "entry", None),
    ("codigo_ucsm", "Código UCSM (10 dígitos)", "entry", None),
    ("escuela", "Escuela profesional", "combo", []),
    ("celular", "Celular (9 dígitos)", "entry", None),
    ("correo", "Correo", "entry", None),
    ("orcid", "ORCID (0000-0000-0000-000X)", "entry", None),
    ("scopus_id", "Scopus ID", "entry", None),
    ("link_cti", "Enlace CTI Vitae (https://...)", "entry", None),
    ("foto", "Foto de perfil (.jpg/.png)", "entry", None),
    ("resumen", "Resumen académico", "texto", 3),
    ("ods", "ODS (selección múltiple)", "lista", [(o, o) for o in ODS]),
    ("intereses", "Intereses (separados por coma)", "entry", None),
]
BLOQUEADOS_AL_EDITAR = ("dni", "codigo_ucsm")


class VistaInvestigadores(ttk.Frame):
    def __init__(self, master, coordinador):
        super().__init__(master, padding=8)
        self.coordinador = coordinador
        self.editando = None                    # codigo UCSM en edicion, o None si es nuevo
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        izquierda = ttk.Frame(self)
        izquierda.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        izquierda.rowconfigure(1, weight=1)
        izquierda.columnconfigure(0, weight=1)
        barra = ttk.Frame(izquierda)
        barra.grid(row=0, column=0, sticky="ew", pady=(0, 6))
        ttk.Label(barra, text="Buscar:").pack(side="left")
        self.busqueda = ttk.Entry(barra, width=28)
        self.busqueda.pack(side="left", padx=6)
        self.busqueda.bind("<Return>", lambda _e: self.refrescar())
        ttk.Button(barra, text="Buscar", command=self.refrescar).pack(side="left")
        self.tabla = Tabla(izquierda, [("codigo", "Código", 90), ("nombre", "Investigador", 230),
                                       ("escuela", "Escuela", 170), ("correo", "Correo", 190),
                                       ("celular", "Celular", 80)], alto=20)
        self.tabla.grid(row=1, column=0, sticky="nsew")
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
        ttk.Button(botones, text="Nuevo", command=self.nuevo).pack(side="left", padx=4)
        ttk.Button(botones, text="Guardar", command=self.guardar).pack(side="left", padx=4)
        ttk.Button(botones, text="Eliminar", command=self.eliminar).pack(side="left", padx=4)
        self.nuevo()

    def refrescar(self):
        ok, filas = ejecutar_seguro(self, investigadores.listar, self.busqueda.get())
        if ok:
            self.tabla.cargar(filas)
        ok, escuelas = ejecutar_seguro(self, investigadores.escuelas)
        if ok:
            self.form.establecer_opciones("escuela", escuelas)

    def nuevo(self):
        self.editando = None
        self.form.bloquear(BLOQUEADOS_AL_EDITAR, False)
        self.form.limpiar()
        self.tabla.deseleccionar()
        self.titulo.set(" Nuevo investigador ")

    def _al_seleccionar(self, _evento=None):
        codigo = self.tabla.seleccionada()
        if not codigo:
            return
        ok, datos = ejecutar_seguro(self, investigadores.obtener, codigo)
        if ok and datos:
            self.form.bloquear(BLOQUEADOS_AL_EDITAR, False)
            self.form.poner(datos)
            self.form.bloquear(BLOQUEADOS_AL_EDITAR, True)
            self.editando = int(codigo)
            self.titulo.set(f" Editando investigador {codigo} ")

    def guardar(self):
        datos = self.form.valores()
        if self.editando is None:
            ok, _ = ejecutar_seguro(self, investigadores.registrar, datos,
                                    self.coordinador["codigo_ucsm"])
            mensaje = "Investigador registrado correctamente."
        else:
            ok, _ = ejecutar_seguro(self, investigadores.modificar, self.editando, datos)
            mensaje = "Investigador modificado correctamente."
        if ok:
            messagebox.showinfo("Investigadores", mensaje, parent=self)
            self.nuevo()
            self.refrescar()

    def eliminar(self):
        if self.editando is None:
            messagebox.showwarning("Investigadores", "Seleccione un investigador de la lista.",
                                   parent=self)
            return
        if not messagebox.askyesno("Eliminar", f"¿Eliminar al investigador {self.editando}?\n"
                                   "Se borrarán también su formato, ODS e intereses.", parent=self):
            return
        ok, _ = ejecutar_seguro(self, investigadores.eliminar, self.editando)
        if ok:
            messagebox.showinfo("Investigadores", "Investigador eliminado.", parent=self)
            self.nuevo()
            self.refrescar()
