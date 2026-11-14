"""
Tema visual del aplicativo: paleta, tipografia y estilos ttk.
Solo usa tkinter de la libreria estandar. Para cambiar los colores basta editar
las constantes de este archivo.
"""
from tkinter import font as tkfont
from tkinter import ttk

AZUL = "#14315C"            # cabecera y encabezados de tabla
AZUL_MEDIO = "#1F4E8C"      # botones principales y pestana activa
AZUL_CLARO = "#3A78C2"      # seleccion y foco
DORADO = "#C9A227"          # acento institucional
FONDO = "#EEF2F7"
TARJETA = "#FFFFFF"
BORDE = "#CBD5E1"
TEXTO = "#1E293B"
TEXTO_SUAVE = "#64748B"
TEXTO_CLARO = "#B9C7DC"     # texto secundario sobre fondo azul
PELIGRO = "#B42318"
PELIGRO_HOVER = "#D92D20"
FILA_ALTERNA = "#F4F7FB"

_familia = "Helvetica"


def fuente(tamano=10, negrita=False):
    """Fuente del aplicativo: (familia, tamano[, 'bold'])."""
    return (_familia, tamano, "bold") if negrita else (_familia, tamano)


def estilo_campo(widget, texto=False):
    """Aspecto plano con borde fino para tk.Text (texto=True) y tk.Listbox."""
    opciones = dict(relief="flat", background="white", foreground=TEXTO, font=fuente(10),
                    highlightthickness=1, highlightbackground=BORDE, highlightcolor=AZUL_CLARO,
                    selectbackground=AZUL_CLARO, selectforeground="white", borderwidth=0)
    if texto:
        opciones.update(padx=6, pady=5)
    else:
        opciones.update(activestyle="none")
    widget.configure(**opciones)


def aplicar(raiz):
    """Configura la ventana raiz y todos los estilos ttk. Llamar una vez, al crear la ventana."""
    global _familia
    disponibles = set(tkfont.families(raiz))
    for candidata in ("Segoe UI", "Helvetica Neue", "Arial", "Helvetica"):
        if candidata in disponibles:
            _familia = candidata
            break
    for nombre in ("TkDefaultFont", "TkTextFont", "TkMenuFont", "TkHeadingFont"):
        tkfont.nametofont(nombre).configure(family=_familia, size=10)

    raiz.configure(background=FONDO)
    raiz.option_add("*TCombobox*Listbox.font", fuente(10))
    raiz.option_add("*TCombobox*Listbox.background", "white")
    raiz.option_add("*TCombobox*Listbox.foreground", TEXTO)
    raiz.option_add("*TCombobox*Listbox.selectBackground", AZUL_CLARO)
    raiz.option_add("*TCombobox*Listbox.selectForeground", "white")

    e = ttk.Style(raiz)
    e.theme_use("clam")      # 'clam' respeta los colores en Windows, Linux y macOS
    e.configure(".", background=FONDO, foreground=TEXTO, font=fuente(10), bordercolor=BORDE)

    # Contenedores y etiquetas
    e.configure("TFrame", background=FONDO)
    e.configure("Tarjeta.TFrame", background=TARJETA)
    e.configure("TLabel", background=FONDO, foreground=TEXTO)
    e.configure("Tarjeta.TLabel", background=TARJETA, foreground=TEXTO)
    e.configure("Titulo.TLabel", background=FONDO, foreground=AZUL, font=fuente(17, True))
    e.configure("Suave.TLabel", background=FONDO, foreground=TEXTO_SUAVE)
    e.configure("TarjetaTitulo.TLabel", background=TARJETA, foreground=AZUL, font=fuente(12, True))
    e.configure("TarjetaSuave.TLabel", background=TARJETA, foreground=TEXTO_SUAVE)

    # Botones
    base = dict(font=fuente(10, True), padding=(16, 7), borderwidth=0, focusthickness=0)
    e.configure("TButton", background="#DDE4EE", foreground=TEXTO, **base)
    e.map("TButton", background=[("active", "#CBD5E1"), ("pressed", "#B8C4D6")])
    e.configure("Primario.TButton", background=AZUL_MEDIO, foreground="white", **base)
    e.map("Primario.TButton", background=[("active", AZUL_CLARO), ("pressed", AZUL)])
    e.configure("Peligro.TButton", background=PELIGRO, foreground="white", **base)
    e.map("Peligro.TButton", background=[("active", PELIGRO_HOVER), ("pressed", "#912018")])
    e.configure("Dorado.TButton", background=DORADO, foreground=AZUL, **base)
    e.map("Dorado.TButton", background=[("active", "#D9B73B"), ("pressed", "#B08E1F")])

    # Campos de texto
    for nombre in ("TEntry", "TCombobox"):
        e.configure(nombre, fieldbackground="white", background="white", foreground=TEXTO,
                    bordercolor=BORDE, lightcolor="white", darkcolor="white", padding=5)
        e.map(nombre, bordercolor=[("focus", AZUL_CLARO)],
              lightcolor=[("focus", AZUL_CLARO)], darkcolor=[("focus", AZUL_CLARO)],
              fieldbackground=[("disabled", FONDO), ("readonly", "white")],
              foreground=[("disabled", TEXTO_SUAVE)])

    # Pestanas
    e.configure("TNotebook", background=FONDO, borderwidth=0, tabmargins=(0, 6, 0, 0))
    e.configure("TNotebook.Tab", background="#DCE3EE", foreground=TEXTO_SUAVE,
                padding=(22, 9), font=fuente(10, True), borderwidth=0)
    e.map("TNotebook.Tab", background=[("selected", AZUL_MEDIO), ("active", "#C7D2E3")],
          foreground=[("selected", "white")])

    # Tablas
    e.configure("Treeview", background="white", fieldbackground="white", foreground=TEXTO,
                rowheight=28, bordercolor=BORDE, borderwidth=1, font=fuente(10))
    e.configure("Treeview.Heading", background=AZUL, foreground="white", font=fuente(10, True),
                padding=(8, 7), relief="flat", borderwidth=0)
    e.map("Treeview.Heading", background=[("active", AZUL_MEDIO)])
    e.map("Treeview", background=[("selected", AZUL_CLARO)], foreground=[("selected", "white")])
    _corregir_colores_treeview(e)

    # Barras de desplazamiento y de progreso
    for orientacion in ("Vertical", "Horizontal"):
        nombre = f"{orientacion}.TScrollbar"
        e.configure(nombre, background="#C3CDDB", troughcolor=FONDO, bordercolor=FONDO,
                    arrowcolor=AZUL, relief="flat")
        e.map(nombre, background=[("active", AZUL_CLARO)])
    e.configure("Barra.Horizontal.TProgressbar", troughcolor="#E2E8F0", background=DORADO,
                bordercolor="#E2E8F0", lightcolor=DORADO, darkcolor=DORADO, thickness=12)


def _corregir_colores_treeview(estilo):
    """Tk 8.6.9 ignora los colores de las filas (tag_configure) si no se aplica este arreglo."""
    def sin_predeterminados(opcion):
        return [f for f in estilo.map("Treeview", query_opt=opcion)
                if f[:2] != ("!disabled", "!selected")]
    estilo.map("Treeview", foreground=sin_predeterminados("foreground"),
               background=sin_predeterminados("background"))
