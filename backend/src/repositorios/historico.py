"""CRUD del historico de publicaciones con sp_cargar_historico (inserta o actualiza)
y sp_eliminar_historico. El procedimiento recibe 33 parametros: aqui se piden al
usuario solo los esenciales y el resto se completa con valores por defecto."""
import hashlib
import uuid as _uuid
from datetime import date

from psycopg2.extras import Json

from ..db.conexion import consultar_dicts, ejecutar_procedimiento
from . import utilidades as u
from .catalogos import TIPOS_PUBLICACION

# Orden EXACTO de los parametros de sp_cargar_historico
ORDEN = [
    "uuid", "title", "publication_year", "type", "volumen", "create_date", "journal_number",
    "create_by", "version", "number_of_pages", "modified_by", "abstract", "total_contributors",
    "peer_review", "pages", "type_discriminator", "bibliographical_note", "visibility",
    "modified_date", "submission_year", "system_name", "portal_url", "sub_title", "language",
    "category", "coordinador", "fecha_reporte", "contributors", "identifiers",
    "electronic_versions", "keywords_groups", "publication_status", "links",
]
ARRAYS = ("contributors", "identifiers", "electronic_versions", "keywords_groups",
          "publication_status")

_SQL_LISTAR = """
SELECT h.uuid::text AS uuid, h.title, h.publication_year, h.type, h.language, h.category
FROM historico h
{filtro}
ORDER BY h.publication_year DESC, h.title
"""

_SQL_OBTENER = """
SELECT h.*, h.uuid::text AS uuid_texto,
  COALESCE((SELECT array_agg(c.contributors ORDER BY c.contributors)
              FROM historico_contributors c WHERE c.uuid = h.uuid), '{}') AS contributors,
  COALESCE((SELECT array_agg(i.identifiers ORDER BY i.identifiers)
              FROM historico_identifiers i WHERE i.uuid = h.uuid), '{}') AS identifiers,
  COALESCE((SELECT array_agg(e.electronic_versions ORDER BY e.electronic_versions)
              FROM historico_electronic_versions e WHERE e.uuid = h.uuid), '{}') AS electronic_versions,
  COALESCE((SELECT array_agg(k.keywords_groups ORDER BY k.keywords_groups)
              FROM historico_keywords_groups k WHERE k.uuid = h.uuid), '{}') AS keywords_groups,
  COALESCE((SELECT array_agg(s.publication_status ORDER BY s.publication_status)
              FROM historico_publication_status s WHERE s.uuid = h.uuid), '{}') AS publication_status,
  COALESCE((SELECT jsonb_agg(jsonb_build_object('pure_id', l.pure_id, 'link_type', l.link_type,
                                               'url', l.url, 'description', l.description))
              FROM historico_links l WHERE l.uuid = h.uuid), '[]'::jsonb) AS links
FROM historico h
WHERE h.uuid = %s::uuid
"""


def listar(filtro=""):
    filtro = (filtro or "").strip()
    if filtro:
        sql = _SQL_LISTAR.format(filtro="WHERE h.title ILIKE %s")
        filas = consultar_dicts(sql, (f"%{filtro}%",))
    else:
        filas = consultar_dicts(_SQL_LISTAR.format(filtro=""))
    return [(f["uuid"], f["title"], f["publication_year"], f["type"], f["language"],
             f["category"]) for f in filas]


def obtener(uuid_texto):
    """Fila completa (claves = columnas de historico) + listas hijas, o None."""
    filas = consultar_dicts(_SQL_OBTENER, (u.obligatorio(uuid_texto, "El UUID"),))
    if not filas:
        return None
    d = filas[0]
    d["uuid"] = d.pop("uuid_texto")
    return d


def para_formulario(d):
    """Convierte lo obtenido en los textos que muestra el formulario."""
    return {
        "title": d["title"], "publication_year": d["publication_year"], "type": d["type"],
        "language": d["language"], "category": d["category"], "volumen": d["volumen"],
        "number_of_pages": d["number_of_pages"], "pages": d["pages"], "abstract": d["abstract"],
        "portal_url": d["portal_url"],
        "contributors": "\n".join(d["contributors"]),
        "identifiers": "; ".join(d["identifiers"]),
        "keywords_groups": "; ".join(d["keywords_groups"]),
    }


def guardar(d, coordinador, uuid_existente=None, fecha_reporte=None):
    """Inserta una publicacion nueva o actualiza la existente (mismo UUID).
    Al actualizar se conservan los campos tecnicos que el usuario no edita."""
    actual = obtener(uuid_existente) if uuid_existente else None
    if uuid_existente and actual is None:
        raise u.ErrorOperacion("La publicacion que intenta modificar ya no existe.")

    def previo(clave, defecto=None):
        return actual[clave] if actual and actual.get(clave) is not None else defecto

    hoy = date.today()
    titulo = u.obligatorio(d.get("title"), "El titulo")
    anio = u.entero(d.get("publication_year"), "El anio de publicacion")
    tipo = u.obligatorio(d.get("type"), "El tipo")
    contribuyentes = u.partir(d.get("contributors"))
    if not contribuyentes:
        raise u.ErrorOperacion("Indique al menos un contribuyente (uno por linea).")
    identificador = uuid_existente or str(_uuid.uuid4())
    if actual:
        fecha_rep = date(actual["anio_reporte"], actual["mes_reporte"], actual["dia_reporte"])
    else:
        fecha_rep = fecha_reporte or hoy

    v = {
        "uuid": identificador, "title": titulo, "publication_year": anio, "type": tipo,
        "volumen": u.entero_opcional(d.get("volumen"), "El volumen"),
        "create_date": previo("create_date", hoy),
        "journal_number": previo("journal_number"),
        "create_by": previo("create_by", "app"),
        # version = hash SHA-1 (40 caracteres hexadecimales) del contenido
        "version": hashlib.sha1(f"{identificador}|{titulo}|{anio}|{hoy}".encode("utf-8")).hexdigest(),
        "number_of_pages": u.entero_opcional(d.get("number_of_pages"), "El total de paginas"),
        "modified_by": "app",
        "abstract": u.texto_opcional(d.get("abstract")),
        "total_contributors": len(contribuyentes),
        "peer_review": previo("peer_review", True),
        "pages": u.texto_opcional(d.get("pages")),
        "type_discriminator": TIPOS_PUBLICACION.get(tipo, "ContributionToJournal"),
        "bibliographical_note": previo("bibliographical_note"),
        "visibility": previo("visibility", "FREE"),
        "modified_date": hoy,
        "submission_year": previo("submission_year", anio),
        "system_name": previo("system_name", "ResearchOutput"),
        "portal_url": u.obligatorio(d.get("portal_url"), "La URL del portal"),
        "sub_title": previo("sub_title"),
        "language": u.obligatorio(d.get("language"), "El idioma"),
        "category": u.obligatorio(d.get("category"), "La categoria"),
        "coordinador": coordinador, "fecha_reporte": fecha_rep,
        "contributors": contribuyentes,
        "identifiers": u.partir(d.get("identifiers")),
        "electronic_versions": previo("electronic_versions", []),
        "keywords_groups": u.partir(d.get("keywords_groups")),
        "publication_status": previo("publication_status", ["Published"]),
        "links": Json(previo("links", [])),
    }
    parametros = [v[k] for k in ORDEN]
    tipos = [None] * len(ORDEN)
    tipos[ORDEN.index("uuid")] = "uuid"
    for k in ARRAYS:
        tipos[ORDEN.index(k)] = "varchar[]"
    tipos[ORDEN.index("links")] = "jsonb"
    ejecutar_procedimiento("sp_cargar_historico", parametros, tipos)
    return identificador


def eliminar(uuid_texto):
    ejecutar_procedimiento("sp_eliminar_historico",
                           [u.obligatorio(uuid_texto, "El UUID")], ["uuid"])
