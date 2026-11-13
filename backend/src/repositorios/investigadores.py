"""CRUD de investigadores. Insertar, modificar y borrar se hacen con procedimientos
almacenados (sp_registrar/modificar/eliminar_investigador); aqui solo se preparan los datos."""
from ..db.conexion import consultar_dicts, ejecutar_procedimiento
from . import utilidades as u

_SQL_LISTAR = """
SELECT i.codigo_ucsm,
       pe.apellido_paterno || ' ' || pe.apellido_materno || ', ' || pe.nombres AS nombre,
       i.escuela_profesional, i.correo_elec, i.n_celular
FROM investigador i
JOIN persona pe ON pe.dni = i.dni
{filtro}
ORDER BY pe.apellido_paterno, pe.apellido_materno, pe.nombres
"""

_SQL_OBTENER = """
SELECT i.codigo_ucsm, pe.dni, pe.nombres, pe.apellido_paterno, pe.apellido_materno,
       pe.genero, pe.fecha_nacimiento,
       i.escuela_profesional AS escuela, i.n_celular AS celular, i.correo_elec AS correo,
       fi.codigo_orcid AS orcid, fi.scopus_id, fi.link_cti_vitae AS link_cti,
       fi.foto_perfil AS foto, fi.resumen_academico AS resumen,
       COALESCE((SELECT array_agg(o.ods ORDER BY o.ods)
                   FROM formato_inv_ods o WHERE o.n_formato_inv = fi.n_formato_inv), '{}') AS ods,
       COALESCE((SELECT array_agg(t.intereses_invest ORDER BY t.intereses_invest)
                   FROM formato_inv_intereses t WHERE t.n_formato_inv = fi.n_formato_inv), '{}') AS intereses
FROM investigador i
JOIN persona pe ON pe.dni = i.dni
JOIN formato_investigador fi ON fi.codigo_ucsm = i.codigo_ucsm
WHERE i.codigo_ucsm = %s
"""


def listar(filtro=""):
    """Filas (codigo, nombre, escuela, correo, celular). filtro busca en nombre o codigo."""
    filtro = (filtro or "").strip()
    if filtro:
        sql = _SQL_LISTAR.format(filtro=(
            "WHERE (pe.nombres || ' ' || pe.apellido_paterno || ' ' || pe.apellido_materno "
            "|| ' ' || i.codigo_ucsm::text) ILIKE %s"))
        filas = consultar_dicts(sql, (f"%{filtro}%",))
    else:
        filas = consultar_dicts(_SQL_LISTAR.format(filtro=""))
    return [(f["codigo_ucsm"], f["nombre"], f["escuela_profesional"], f["correo_elec"],
             f["n_celular"]) for f in filas]


def opciones():
    """Pares (codigo, 'codigo - nombre') para elegir inventores en patentes."""
    return [(f[0], f"{f[0]} - {f[1]}") for f in listar()]


def escuelas():
    filas = consultar_dicts("SELECT DISTINCT escuela_profesional FROM investigador "
                            "ORDER BY escuela_profesional")
    return [f["escuela_profesional"] for f in filas]


def obtener(codigo):
    """Todos los datos de un investigador (claves iguales a las del formulario) o None."""
    filas = consultar_dicts(_SQL_OBTENER, (u.entero(codigo, "El codigo UCSM"),))
    if not filas:
        return None
    d = filas[0]
    d["intereses"] = ", ".join(d["intereses"])
    return d


def _datos_comunes(d):
    return dict(
        nombres=u.obligatorio(d.get("nombres"), "Los nombres"),
        ap_pat=u.obligatorio(d.get("apellido_paterno"), "El apellido paterno"),
        ap_mat=u.obligatorio(d.get("apellido_materno"), "El apellido materno"),
        genero=u.obligatorio(d.get("genero"), "El genero"),
        nacimiento=u.fecha(d.get("fecha_nacimiento"), "La fecha de nacimiento"),
        escuela=u.obligatorio(d.get("escuela"), "La escuela profesional"),
        celular=u.entero(d.get("celular"), "El celular"),
        correo=u.obligatorio(d.get("correo"), "El correo"),
        orcid=u.obligatorio(d.get("orcid"), "El ORCID"),
        scopus=u.entero(d.get("scopus_id"), "El Scopus ID"),
        link=u.obligatorio(d.get("link_cti"), "El enlace CTI Vitae"),
        resumen=u.obligatorio(d.get("resumen"), "El resumen academico"),
        foto=u.obligatorio(d.get("foto"), "La foto de perfil"),
        ods=list(d.get("ods") or []),
        intereses=u.partir(d.get("intereses"), con_comas=True),
    )


def registrar(d, coordinador):
    c = _datos_comunes(d)
    parametros = [
        u.obligatorio(d.get("dni"), "El DNI"), c["nombres"], c["ap_pat"], c["ap_mat"],
        c["genero"], c["nacimiento"],
        u.entero(d.get("codigo_ucsm"), "El codigo UCSM"), c["escuela"], c["celular"], c["correo"],
        c["orcid"], c["scopus"], c["link"], c["resumen"], c["foto"],
        coordinador, c["ods"], c["intereses"],
    ]
    ejecutar_procedimiento("sp_registrar_investigador", parametros,
                           [None] * 16 + ["varchar[]", "varchar[]"])


def modificar(codigo, d):
    c = _datos_comunes(d)
    parametros = [
        u.entero(codigo, "El codigo UCSM"), c["nombres"], c["ap_pat"], c["ap_mat"],
        c["genero"], c["nacimiento"], c["escuela"], c["celular"], c["correo"],
        c["orcid"], c["scopus"], c["link"], c["resumen"], c["foto"],
        c["ods"], c["intereses"],
    ]
    ejecutar_procedimiento("sp_modificar_investigador", parametros,
                           [None] * 14 + ["varchar[]", "varchar[]"])


def eliminar(codigo):
    ejecutar_procedimiento("sp_eliminar_investigador", [u.entero(codigo, "El codigo UCSM")])
