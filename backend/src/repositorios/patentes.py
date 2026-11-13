"""CRUD de patentes con procedimientos (sp_registrar/modificar/eliminar_patente)."""
from ..db.conexion import consultar_dicts, ejecutar_procedimiento
from . import utilidades as u

_SQL_LISTAR = """
SELECT pa.n_patente, pa.titulo_patente, pa.fecha_registro, pa.pais,
       COALESCE((SELECT string_agg(i.inventores, '; ' ORDER BY i.inventores)
                   FROM formato_paten_inventores i
                  WHERE i.n_formato_pat = fp.n_formato_pat), '') AS inventores
FROM patente pa
JOIN formato_patente fp ON fp.n_patente = pa.n_patente
ORDER BY pa.fecha_registro DESC, pa.n_patente
"""

_SQL_OBTENER = """
SELECT pa.n_patente, pa.titulo_patente AS titulo, pa.editorial, pa.fecha_registro,
       pa.cip, pa.pais,
       COALESCE((SELECT array_agg(fi.codigo_ucsm ORDER BY fi.codigo_ucsm)
                   FROM formato_patente_investigador fpi
                   JOIN formato_investigador fi ON fi.n_formato_inv = fpi.n_formato_inv
                  WHERE fpi.n_formato_pat = fp.n_formato_pat), '{}') AS inventores,
       COALESCE((SELECT array_agg(o.campo_ocde ORDER BY o.campo_ocde)
                   FROM formato_paten_ocde o WHERE o.n_formato_pat = fp.n_formato_pat), '{}') AS campos,
       COALESCE((SELECT array_agg(o.objetivos_ocde ORDER BY o.campo_ocde)
                   FROM formato_paten_ocde o WHERE o.n_formato_pat = fp.n_formato_pat), '{}') AS objetivos
FROM patente pa
JOIN formato_patente fp ON fp.n_patente = pa.n_patente
WHERE pa.n_patente = %s
"""


def listar():
    return [(f["n_patente"], f["titulo_patente"], f["fecha_registro"], f["pais"], f["inventores"])
            for f in consultar_dicts(_SQL_LISTAR)]


def obtener(n_patente):
    filas = consultar_dicts(_SQL_OBTENER, (u.obligatorio(n_patente, "El numero de patente"),))
    if not filas:
        return None
    d = filas[0]
    d["ocde"] = "\n".join(f"{c} | {o}" for c, o in zip(d.pop("campos"), d.pop("objetivos")))
    return d


def _ocde(texto):
    """Cada linea: 'campo | objetivo'. Devuelve (campos, objetivos)."""
    campos, objetivos = [], []
    for linea in u.partir(texto):
        if "|" not in linea:
            raise u.ErrorOperacion(f"Linea OCDE invalida '{linea}': use 'campo | objetivo'.")
        campo, objetivo = (x.strip() for x in linea.split("|", 1))
        if not campo or not objetivo:
            raise u.ErrorOperacion(f"Linea OCDE incompleta: '{linea}'.")
        campos.append(campo)
        objetivos.append(objetivo)
    return campos, objetivos


def _inventores(d):
    return [u.entero(c, "El codigo del inventor") for c in (d.get("inventores") or [])]


def registrar(d, coordinador):
    campos, objetivos = _ocde(d.get("ocde"))
    parametros = [
        u.obligatorio(d.get("n_patente"), "El numero de patente"),
        u.obligatorio(d.get("titulo"), "El titulo"),
        u.obligatorio(d.get("editorial"), "La editorial"),
        u.fecha(d.get("fecha_registro"), "La fecha de registro"),
        u.obligatorio(d.get("cip"), "El CIP"),
        u.obligatorio(d.get("pais"), "El pais"),
        coordinador, _inventores(d), campos, objetivos,
    ]
    ejecutar_procedimiento("sp_registrar_patente", parametros,
                           [None] * 7 + ["bigint[]", "varchar[]", "varchar[]"])


def modificar(n_patente, d):
    campos, objetivos = _ocde(d.get("ocde"))
    parametros = [
        u.obligatorio(n_patente, "El numero de patente"),
        u.obligatorio(d.get("titulo"), "El titulo"),
        u.obligatorio(d.get("editorial"), "La editorial"),
        u.fecha(d.get("fecha_registro"), "La fecha de registro"),
        u.obligatorio(d.get("cip"), "El CIP"),
        u.obligatorio(d.get("pais"), "El pais"),
        _inventores(d), campos, objetivos,
    ]
    ejecutar_procedimiento("sp_modificar_patente", parametros,
                           [None] * 6 + ["bigint[]", "varchar[]", "varchar[]"])


def eliminar(n_patente):
    ejecutar_procedimiento("sp_eliminar_patente",
                           [u.obligatorio(n_patente, "El numero de patente")])