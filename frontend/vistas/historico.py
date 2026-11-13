"""Pestana Historico: publicaciones (cargar, modificar y eliminar)."""
import tkinter as tk
from tkinter import messagebox, ttk

from backend.src.repositorios import historico
from backend.src.repositorios.catalogos import CATEGORIAS, IDIOMAS, TIPOS_PUBLICACION

from .widgets import Formulario, Tabla, ejecutar_seguro

CAMPOS = [
    ("title", "Título", "entry", None),
    ("publication_year", "Año de publicación", "entry", None),
    ("type", "Tipo", "combo", list(TIPOS_PUBLICACION)),
    ("language", "Idioma", "combo", IDIOMAS),
    ("category", "Categoría", "combo", CATEGORIAS),
    ("volumen", "Volumen (opcional)", "entry", None),
    ("number_of_pages", "Total de páginas (opcional)", "entry", None),
    ("pages", "Páginas (ej. 221-229)", "entry", None),
    ("portal_url", "URL del portal (http...)", "entry", None),
    ("abstract", "Resumen", "texto", 4),
    ("contributors", "Contribuyentes\n(uno por línea)", "texto", 3),
    ("identifiers", "Identificadores (separados por ;)", "entry", None),
    ("keywords_groups", "Palabras clave (separadas por ;)", "entry", None),
]


class VistaHistorico(ttk.Frame):
    def __init__(self, master, coordinador):
        super().__init__(master, padding=8)
        self.coordinador = coordinador
        self.editando = None                    # UUID en edicion
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        izquierda = ttk.Frame(self)
        izquierda.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        izquierda.rowconfigure(1, weight=1)
        izquierda.columnconfigure(0, weight=1)
        barra = ttk.Frame(izquierda)
        barra.grid(row=0, column=0, sticky="ew", pady=(0, 6))
        ttk.Label(barra, text="Buscar por título:").pack(side="left")
        self.busqueda = ttk.Entry(barra, width=30)
        self.busqueda.pack(side="left", padx=6)
        self.busqueda.bind("<Return>", lambda _e: self.refrescar())
        ttk.Button(barra, text="Buscar", command=self.refrescar).pack(side="left")
        self.tabla = Tabla(izquierda, [("uuid", "UUID", 110), ("titulo", "Título", 330),
                                       ("anio", "Año", 50), ("tipo", "Tipo", 100),
                                       ("idioma", "Idioma", 70), ("categoria", "Categoría", 80)],
                           alto=20)
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
        ttk.Button(botones, text="Nueva", command=self.nueva).pack(side="left", padx=4)
        ttk.Button(botones, text="Guardar", command=self.guardar).pack(side="left", padx=4)
        ttk.Button(botones, text="Eliminar", command=self.eliminar).pack(side="left", padx=4)
        self.nueva()

    def refrescar(self):
        ok, filas = ejecutar_seguro(self, historico.listar, self.busqueda.get())
        if ok:
            self.tabla.cargar(filas)

    def nueva(self):
        self.editando = None
        self.form.limpiar()
        self.form.poner({"type": "Article", "language": "English", "category": "Research"})
        self.tabla.deseleccionar()
        self.titulo.set(" Nueva publicación ")

    def _al_seleccionar(self, _evento=None):
        uuid = self.tabla.seleccionada()
        if not uuid:
            return
        ok, datos = ejecutar_seguro(self, historico.obtener, uuid)
        if ok and datos:
            self.form.poner(historico.para_formulario(datos))
            self.editando = uuid
            self.titulo.set(f" Editando publicación {uuid[:8]}… ")

    def guardar(self):
        datos = self.form.valores()
        ok, _ = ejecutar_seguro(self, historico.guardar, datos, self.coordinador["codigo_ucsm"],
                                uuid_existente=self.editando)
        if ok:
            messagebox.showinfo("Histórico", "Publicación guardada correctamente.", parent=self)
            self.nueva()
            self.refrescar()

    def eliminar(self):
        if self.editando is None:
            messagebox.showwarning("Histórico", "Seleccione una publicación de la lista.", parent=self)
            return
        if not messagebox.askyesno("Eliminar", "¿Eliminar esta publicación?\n"
                                   "Se borrarán también sus contribuyentes, enlaces y palabras clave.",
                                   parent=self):
            return
        ok, _ = ejecutar_seguro(self, historico.eliminar, self.editando)
        if ok:
            messagebox.showinfo("Histórico", "Publicación eliminada.", parent=self)
            self.nueva()
            self.refrescar()
