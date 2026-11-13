"""Conversion y validacion basica de lo que escribe el usuario (antes de llegar a la base)."""
import re
from datetime import date, datetime

from ..db.conexion import ErrorOperacion


def obligatorio(valor, campo):
    texto = str(valor if valor is not None else "").strip()
    if not texto:
        raise ErrorOperacion(f"{campo} es obligatorio.")
    return texto


def texto_opcional(valor):
    texto = str(valor if valor is not None else "").strip()
    return texto or None


def entero(valor, campo):
    try:
        return int(str(valor).strip())
    except (TypeError, ValueError):
        raise ErrorOperacion(f"{campo} debe ser un numero entero.") from None


def entero_opcional(valor, campo):
    if valor is None or str(valor).strip() == "":
        return None
    return entero(valor, campo)


def fecha(valor, campo):
    if isinstance(valor, datetime):
        return valor.date()
    if isinstance(valor, date):
        return valor
    texto = str(valor if valor is not None else "").strip()
    for formato in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(texto, formato).date()
        except ValueError:
            pass
    raise ErrorOperacion(f"{campo} debe tener el formato AAAA-MM-DD.")


def partir(texto, con_comas=False):
    """Separa por ';' y saltos de linea (y por ',' si con_comas). Quita vacios y repetidos."""
    patron = r"[,;\n]+" if con_comas else r"[;\n]+"
    resultado = []
    for parte in re.split(patron, texto or ""):
        parte = parte.strip()
        if parte and parte not in resultado:
            resultado.append(parte)
    return resultado