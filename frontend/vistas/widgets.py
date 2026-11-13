"""Componentes reutilizables de la interfaz (solo Tkinter/ttk de la libreria estandar)."""
import tkinter as tk
from tkinter import messagebox, ttk

from backend.src.db.conexion import ErrorConexion


def ejecutar_seguro(ventana, funcion, *args, **kwargs):
    """Ejecuta funcion y, si falla, muestra el mensaje al usuario. Devuelve (ok, resultado)."""
    try:
        return True, funcion(*args, **kwargs)
    except ErrorConexion as e:
        messagebox.showerror("No se pudo completar la operación", str(e), parent=ventana)
    except Exception as e:                       # error inesperado: no dejar la ventana muda
        messagebox.showerror("Error inesperado", f"{type(e).__name__}: {e}", parent=ventana)
    return False, None


class Tabla(ttk.Frame):
    """Treeview con barras de desplazamiento. Las filas se identifican por su primer valor."""

    def __init__(self, master, columnas=(), alto=12):
        super().__init__(master)
        self.arbol = ttk.Treeview(self, show="headings", height=alto, selectmode="browse")
        vertical = ttk.Scrollbar(self, orient="vertical", command=self.arbol.yview)
        horizontal = ttk.Scrollbar(self, orient="horizontal", command=self.arbol.xview)
        self.arbol.configure(yscrollcommand=vertical.set, xscrollcommand=horizontal.set)
        self.arbol.grid(row=0, column=0, sticky="nsew")
        vertical.grid(row=0, column=1, sticky="ns")
        horizontal.grid(row=1, column=0, sticky="ew")
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.configurar(columnas)

    def configurar(self, columnas):
        """columnas: lista de (id, titulo, ancho)."""
        self.limpiar()
        self.arbol.configure(columns=[c[0] for c in columnas])
        for cid, titulo, ancho in columnas:
            self.arbol.heading(cid, text=titulo)
            self.arbol.column(cid, width=ancho, minwidth=60, stretch=True)

    def limpiar(self):
        self.arbol.delete(*self.arbol.get_children())

    def cargar(self, filas, con_id=True):
        """con_id=True: el primer valor de cada fila es su identificador (se recupera con
        seleccionada()). Usar con_id=False cuando la primera columna puede repetirse."""
        self.limpiar()
        for fila in filas:
            valores = ["" if v is None else v for v in fila]
            if con_id:
                self.arbol.insert("", "end", iid=str(fila[0]), values=valores)
            else:
                self.arbol.insert("", "end", values=valores)

    def seleccionada(self):
        seleccion = self.arbol.selection()
        return seleccion[0] if seleccion else None

    def deseleccionar(self):
        self.arbol.selection_remove(*self.arbol.selection())


class Formulario(ttk.Frame):
    """Formulario generado a partir de una lista de campos.
    campos: (clave, etiqueta, tipo, extra) con tipo en entry | combo | texto | lista
      combo -> extra = valores; texto -> extra = alto en lineas;
      lista -> extra = [(valor, etiqueta), ...] con seleccion multiple."""

    def __init__(self, master, campos):
        super().__init__(master)
        self.widgets, self.tipos, self.opciones = {}, {}, {}
        for fila, (clave, etiqueta, tipo, extra) in enumerate(campos):
            ttk.Label(self, text=etiqueta).grid(row=fila, column=0, sticky="nw", padx=(0, 8), pady=2)
            if tipo == "combo":
                w = ttk.Combobox(self, values=list(extra or []), width=38)
            elif tipo == "texto":
                w = tk.Text(self, width=40, height=extra or 3, wrap="word")
            elif tipo == "lista":
                self.opciones[clave] = list(extra or [])
                w = tk.Listbox(self, selectmode="multiple", exportselection=False, width=44,
                               height=min(6, max(3, len(self.opciones[clave]))))
                self._llenar_lista(w, self.opciones[clave])
            else:
                w = ttk.Entry(self, width=40)
            w.grid(row=fila, column=1, sticky="w", pady=2)
            self.widgets[clave], self.tipos[clave] = w, tipo

    @staticmethod
    def _llenar_lista(w, opciones):
        w.delete(0, "end")
        for _valor, etiqueta in opciones:
            w.insert("end", etiqueta)

    def establecer_opciones(self, clave, opciones, conservar=True):
        """Cambia las opciones de un campo combo o lista."""
        if self.tipos[clave] == "combo":
            self.widgets[clave].configure(values=list(opciones))
            return
        elegidos = self.valores()[clave] if conservar else []
        self.opciones[clave] = list(opciones)
        self._llenar_lista(self.widgets[clave], self.opciones[clave])
        self._seleccionar(clave, elegidos)

    def _seleccionar(self, clave, valores):
        w = self.widgets[clave]
        w.selection_clear(0, "end")
        for i, (valor, _etiqueta) in enumerate(self.opciones[clave]):
            if valor in (valores or []):
                w.selection_set(i)

    def valores(self):
        resultado = {}
        for clave, w in self.widgets.items():
            tipo = self.tipos[clave]
            if tipo == "texto":
                resultado[clave] = w.get("1.0", "end").strip()
            elif tipo == "lista":
                resultado[clave] = [self.opciones[clave][i][0] for i in w.curselection()]
            else:
                resultado[clave] = w.get().strip()
        return resultado

    def poner(self, datos):
        """Rellena el formulario con un dict (clave -> valor). Las claves ausentes se vacian."""
        for clave, w in self.widgets.items():
            valor = datos.get(clave)
            tipo = self.tipos[clave]
            if tipo == "lista":
                self._seleccionar(clave, valor if isinstance(valor, list) else [])
                continue
            texto = "" if valor is None else str(valor)
            if tipo == "texto":
                w.delete("1.0", "end")
                w.insert("1.0", texto)
            else:                                # entry y combo (aunque esten bloqueados)
                anterior = str(w.cget("state"))
                w.configure(state="normal")
                if tipo == "combo":
                    w.set(texto)
                else:
                    w.delete(0, "end")
                    w.insert(0, texto)
                w.configure(state=anterior)

    def limpiar(self):
        self.poner({})

    def bloquear(self, claves, bloqueado=True):
        for clave in claves:
            self.widgets[clave].configure(state="disabled" if bloqueado else "normal")
