"""Componentes reutilizables de la interfaz (solo Tkinter/ttk de la libreria estandar)."""
import tkinter as tk
from tkinter import messagebox, ttk

from backend.src.db.conexion import ErrorConexion

from .. import estilos


def ejecutar_seguro(ventana, funcion, *args, **kwargs):
    """Ejecuta funcion y, si falla, muestra el mensaje al usuario. Devuelve (ok, resultado)."""
    try:
        return True, funcion(*args, **kwargs)
    except ErrorConexion as e:
        messagebox.showerror("No se pudo completar la operación", str(e), parent=ventana)
    except Exception as e:                       # error inesperado: no dejar la ventana muda
        messagebox.showerror("Error inesperado", f"{type(e).__name__}: {e}", parent=ventana)
    return False, None


class Tarjeta(tk.Frame):
    """Panel blanco con borde fino. Los widgets ttk se agregan en .cuerpo (usar los estilos
    'Tarjeta.TFrame', 'Tarjeta.TLabel', etc.). .titulo es un StringVar con el titulo del panel."""

    def __init__(self, master, titulo=None, padding=14):
        super().__init__(master, background=estilos.TARJETA, highlightthickness=1,
                         highlightbackground=estilos.BORDE, borderwidth=0)
        self.cuerpo = ttk.Frame(self, style="Tarjeta.TFrame", padding=padding)
        self.cuerpo.pack(fill="both", expand=True)
        self.titulo = tk.StringVar(value=titulo or "")
        if titulo is not None:
            ttk.Label(self.cuerpo, textvariable=self.titulo, style="TarjetaTitulo.TLabel").pack(
                anchor="w", pady=(0, 10))


class Desplazable(ttk.Frame):
    """Zona con barra de desplazamiento vertical y rueda del raton: lo que no cabe en la
    ventana se desplaza en vez de cortarse. Los widgets se colocan dentro de .cuerpo.
    ajustar_ancho=True: el contenido se estira al ancho disponible (paginas completas);
    False: el ancho se adapta al contenido (formularios)."""

    def __init__(self, master, fondo=estilos.FONDO, estilo="TFrame", padding=0, ajustar_ancho=False):
        super().__init__(master)
        self._ajustar_ancho = ajustar_ancho
        self.lienzo = tk.Canvas(self, background=fondo, highlightthickness=0, borderwidth=0, height=120)
        barra = ttk.Scrollbar(self, orient="vertical", command=self.lienzo.yview)
        self.lienzo.configure(yscrollcommand=barra.set)
        barra.pack(side="right", fill="y")
        self.lienzo.pack(side="left", fill="both", expand=True)
        self.cuerpo = ttk.Frame(self.lienzo, style=estilo, padding=padding)
        self._ventana = self.lienzo.create_window((0, 0), window=self.cuerpo, anchor="nw")
        self.cuerpo.bind("<Configure>", self._al_cambiar_cuerpo)
        self.lienzo.bind("<Configure>", self._al_cambiar_lienzo)
        for secuencia in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
            self.bind_all(secuencia, self._rueda, add="+")

    def _al_cambiar_cuerpo(self, evento):
        self.lienzo.configure(scrollregion=self.lienzo.bbox("all"))
        if not self._ajustar_ancho:
            self.lienzo.configure(width=evento.width)

    def _al_cambiar_lienzo(self, evento):
        if self._ajustar_ancho:
            self.lienzo.itemconfigure(self._ventana, width=evento.width)

    def _rueda(self, evento):
        """Desplaza solo si el puntero esta sobre esta zona (y no sobre una lista o texto,
        que se desplazan por su cuenta)."""
        try:
            if not self.winfo_exists():
                return
            destino = self.winfo_containing(evento.x_root, evento.y_root)
        except (tk.TclError, KeyError):          # p. ej. la lista desplegable de un combo
            return
        if isinstance(destino, (tk.Listbox, tk.Text)):
            return
        while destino is not None and destino is not self:
            destino = destino.master
        if destino is None or self.lienzo.yview() == (0.0, 1.0):
            return
        sentido = -1 if (evento.num == 4 or evento.delta > 0) else 1
        self.lienzo.yview_scroll(sentido * 3, "units")


class PanelFormulario(tk.Frame):
    """Tarjeta para formularios largos: titulo arriba, centro con desplazamiento (.cuerpo)
    y pie fijo para los botones (.pie), que siempre quedan a la vista."""

    def __init__(self, master):
        super().__init__(master, background=estilos.TARJETA, highlightthickness=1,
                         highlightbackground=estilos.BORDE, borderwidth=0)
        self.titulo = tk.StringVar()
        ttk.Label(self, textvariable=self.titulo, style="TarjetaTitulo.TLabel").pack(
            anchor="w", padx=14, pady=(12, 4))
        self.zona = Desplazable(self, fondo=estilos.TARJETA, estilo="Tarjeta.TFrame", padding=(14, 6))
        self.zona.pack(fill="both", expand=True)
        self.cuerpo = self.zona.cuerpo
        tk.Frame(self, background=estilos.BORDE, height=1).pack(fill="x")
        self.pie = ttk.Frame(self, style="Tarjeta.TFrame", padding=(14, 10))
        self.pie.pack(fill="x")


class Encabezado(ttk.Frame):
    """Titulo de pestana con una linea de descripcion debajo."""

    def __init__(self, master, titulo, descripcion):
        super().__init__(master)
        ttk.Label(self, text=titulo, style="Titulo.TLabel").pack(anchor="w")
        ttk.Label(self, text=descripcion, style="Suave.TLabel").pack(anchor="w", pady=(0, 2))


class Tabla(ttk.Frame):
    """Treeview con barras de desplazamiento y filas alternas. Las filas se identifican
    por su primer valor."""

    def __init__(self, master, columnas=(), alto=8):
        super().__init__(master)
        self.arbol = ttk.Treeview(self, show="headings", height=alto, selectmode="browse")
        self.arbol.tag_configure("alterna", background=estilos.FILA_ALTERNA)
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
        for numero, fila in enumerate(filas):
            valores = ["" if v is None else v for v in fila]
            etiquetas = ("alterna",) if numero % 2 else ()
            if con_id:
                self.arbol.insert("", "end", iid=str(fila[0]), values=valores, tags=etiquetas)
            else:
                self.arbol.insert("", "end", values=valores, tags=etiquetas)

    def seleccionada(self):
        seleccion = self.arbol.selection()
        return seleccion[0] if seleccion else None

    def deseleccionar(self):
        self.arbol.selection_remove(*self.arbol.selection())


class Formulario(ttk.Frame):
    """Formulario generado a partir de una lista de campos (para colocar dentro de una Tarjeta).
    campos: (clave, etiqueta, tipo, extra) con tipo en entry | combo | texto | lista
      combo -> extra = valores; texto -> extra = alto en lineas;
      lista -> extra = [(valor, etiqueta), ...] con seleccion multiple."""

    def __init__(self, master, campos):
        super().__init__(master, style="Tarjeta.TFrame")
        self.widgets, self.tipos, self.opciones = {}, {}, {}
        for fila, (clave, etiqueta, tipo, extra) in enumerate(campos):
            ttk.Label(self, text=etiqueta, style="Tarjeta.TLabel").grid(
                row=fila, column=0, sticky="nw", padx=(0, 10), pady=3)
            if tipo == "combo":
                w = ttk.Combobox(self, values=list(extra or []), width=34)
                # la rueda del raton desplaza el formulario, no cambia el valor del combo
                for secuencia in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
                    w.bind(secuencia, lambda _e: "break")
            elif tipo == "texto":
                w = tk.Text(self, width=36, height=extra or 3, wrap="word")
                estilos.estilo_campo(w, texto=True)
            elif tipo == "lista":
                self.opciones[clave] = list(extra or [])
                w = tk.Listbox(self, selectmode="multiple", exportselection=False, width=40,
                               height=min(6, max(3, len(self.opciones[clave]))))
                estilos.estilo_campo(w)
                self._llenar_lista(w, self.opciones[clave])
            else:
                w = ttk.Entry(self, width=36)
            w.grid(row=fila, column=1, sticky="w", pady=3)
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
