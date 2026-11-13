"""
Acceso nativo a PostgreSQL con psycopg2 (sin frameworks ni ORM).

Todo el aplicativo (ventana, pruebas e instalador) usa este modulo:
  - conectar / probar_conexion        -> avance anterior (conexion)
  - ejecutar_consulta / consultar_dicts -> SELECT (reportes y listados)
  - ejecutar_procedimiento            -> CALL sp_...  (insertar, modificar, borrar)
  - ejecutar_sentencia                -> DML suelto (solo para pruebas)
"""
import configparser
import os
import re
import sys

import psycopg2

CLAVES_OBLIGATORIAS = ("host", "port", "dbname", "user", "password")
_NOMBRE_SQL = re.compile(r"^[a-z_][a-z0-9_]*$")


class ErrorConexion(Exception):
    """Error de conexion o de configuracion con mensaje listo para mostrar."""


class ErrorOperacion(ErrorConexion):
    """Operacion rechazada por la base (validacion, restriccion, procedimiento o trigger).
    Hereda de ErrorConexion para que las pantallas capturen un unico tipo de error."""


# Mensajes amigables para las restricciones CHECK mas comunes (nombre -> texto).
MENSAJES_RESTRICCION = {
    "ck_persona_dni": "El DNI debe tener exactamente 8 digitos.",
    "persona_genero_check": "El genero debe ser Femenino o Masculino.",
    "persona_fecha_nacimiento_check": "La fecha de nacimiento debe ser anterior a hoy.",
    "ck_investigador_codigo": "El codigo UCSM debe tener 10 digitos.",
    "ck_investigador_celular": "El celular debe tener 9 digitos y empezar con 9.",
    "ck_investigador_correo": "El correo no tiene un formato valido.",
    "ck_formato_inv_orcid": "El ORCID debe tener el formato 0000-0000-0000-000X.",
    "ck_formato_inv_scopus": "El Scopus ID debe ser mayor que 0.",
    "ck_formato_inv_link": "El enlace CTI Vitae debe empezar con https://",
    "ck_formato_inv_foto": "La foto debe ser un archivo .jpg, .jpeg o .png.",
    "ck_formato_inv_ods_ods": "El ODS debe tener el formato 'ODS n: nombre' (n de 1 a 17).",
    "ck_patente_id": "El numero de patente debe tener el formato PE-123456.",
    "patente_fecha_registro_check": "La fecha de registro de la patente no puede ser futura.",
    "historico_publication_year_check": "El anio de publicacion debe estar entre 1900 y 2100.",
    "historico_version_check": "La version debe ser un hash de 40 caracteres hexadecimales.",
    "historico_portal_url_check": "La URL del portal debe empezar con http.",
    "historico_submission_year_check": "El anio de envio debe estar entre 1900 y 2100.",
    "historico_total_number_of_contributors_check": "Debe haber al menos un contribuyente.",
    "historico_volumen_check": "El volumen debe ser mayor que 0.",
    "historico_number_of_pages_check": "El numero de paginas debe ser mayor que 0.",
}


def carpeta_base():
    """Carpeta donde vive config.ini: backend o junto al .exe."""
    if getattr(sys, "frozen", False):          # ejecutable generado con PyInstaller
        return os.path.dirname(sys.executable)
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def leer_configuracion(ruta=None):
    """Devuelve un dict con los datos de conexion tomados de config.ini."""
    ruta = ruta or os.path.join(carpeta_base(), "config.ini")
    if not os.path.isfile(ruta):
        raise ErrorConexion(
            f"No se encontro {ruta}. Copie config.ini.example como config.ini "
            "y complete los datos."
        )
    lector = configparser.ConfigParser()
    lector.read(ruta, encoding="utf-8")
    if not lector.has_section("postgresql"):
        raise ErrorConexion("config.ini no tiene la seccion [postgresql].")
    cfg = dict(lector["postgresql"])
    cfg["password"] = os.environ.get("UCSM_DB_PASSWORD", cfg.get("password", ""))
    faltan = [k for k in CLAVES_OBLIGATORIAS if not cfg.get(k)]
    if faltan:
        raise ErrorConexion("Faltan datos en config.ini: " + ", ".join(faltan))
    return cfg


def conectar(cfg=None):
    """Abre y devuelve una conexion. Quien la llama debe cerrarla."""
    cfg = cfg or leer_configuracion()
    try:
        return psycopg2.connect(
            host=cfg["host"],
            port=int(cfg["port"]),
            dbname=cfg["dbname"],
            user=cfg["user"],
            password=cfg["password"],
            connect_timeout=int(cfg.get("connect_timeout", 5)),
            client_encoding="UTF8",
        )
    except psycopg2.OperationalError as e:
        raise ErrorConexion(_explicar(str(e))) from e
    except ValueError as e:                      # puerto o timeout no numericos
        raise ErrorConexion("El puerto y el tiempo de espera deben ser numeros.") from e


def _explicar(mensaje):
    """Traduce los errores mas comunes de conexion a un mensaje entendible."""
    m = mensaje.lower()
    if "password authentication failed" in m:
        return "Usuario o contrasenia incorrectos."
    if "does not exist" in m and "database" in m:
        return "La base de datos no existe. Cree la base y ejecute instalar_bd.py."
    if "connection refused" in m or "could not connect" in m:
        return "No se pudo conectar: verifique que PostgreSQL este iniciado y que host y puerto sean correctos."
    if "timeout" in m:
        return "Tiempo de espera agotado al conectar con el servidor."
    return "Error de conexion: " + mensaje.strip()


def _mensaje_operacion(e):
    """Convierte un error de psycopg2 en un texto para el usuario.
    Los RAISE EXCEPTION de procedimientos y triggers ya vienen redactados."""
    diag = getattr(e, "diag", None)
    restriccion = getattr(diag, "constraint_name", None)
    if restriccion in MENSAJES_RESTRICCION:
        return MENSAJES_RESTRICCION[restriccion]
    codigo = getattr(e, "pgcode", None)
    primario = (getattr(diag, "message_primary", None) or str(e)).strip()
    detalle = f" ({restriccion})" if restriccion else ""
    if codigo == "23505":
        return "Ya existe un registro con esos datos" + detalle + "."
    if codigo == "23503":
        return "La operacion se relaciona con otros registros (clave foranea)" + detalle + "."
    if codigo == "23514":
        return "Dato invalido" + detalle + "."
    if codigo in ("22P02", "22007", "22008", "22001", "22003"):
        return "Formato o tamanio de dato invalido: " + primario
    return primario


def ejecutar_consulta(sql, parametros=None, cfg=None):
    """Ejecuta un SELECT y devuelve (nombres_de_columnas, filas)."""
    conn = conectar(cfg)
    try:
        with conn.cursor() as cur:
            cur.execute(sql, parametros)
            columnas = [d[0] for d in cur.description]
            return columnas, cur.fetchall()
    except psycopg2.Error as e:
        raise ErrorOperacion(_mensaje_operacion(e)) from e
    finally:
        conn.close()


def consultar_dicts(sql, parametros=None, cfg=None):
    """Como ejecutar_consulta, pero devuelve una lista de diccionarios."""
    columnas, filas = ejecutar_consulta(sql, parametros, cfg)
    return [dict(zip(columnas, fila)) for fila in filas]


def ejecutar_procedimiento(nombre, parametros=(), tipos=None, cfg=None):
    """
    Ejecuta CALL nombre(%s, %s, ...) en una transaccion propia.
    Hace commit si todo sale bien y rollback si algo falla (incluidos los
    triggers diferidos, que se validan en el commit).
      tipos: lista opcional (misma longitud que parametros) con un cast por
             parametro, p. ej. "varchar[]", "uuid", "jsonb"; None = sin cast.
    Lanza ErrorOperacion con un mensaje listo para mostrar.
    """
    if not _NOMBRE_SQL.match(nombre):
        raise ValueError("Nombre de procedimiento invalido: " + nombre)
    parametros = tuple(parametros)
    tipos = list(tipos) if tipos else [None] * len(parametros)
    if len(tipos) != len(parametros):
        raise ValueError("tipos y parametros deben tener la misma longitud")
    marcas = ", ".join("%s" + ("::" + t if t else "") for t in tipos)
    conn = conectar(cfg)
    try:
        with conn.cursor() as cur:
            cur.execute(f"CALL {nombre}({marcas})", parametros)
        conn.commit()
    except psycopg2.Error as e:
        conn.rollback()
        raise ErrorOperacion(_mensaje_operacion(e)) from e
    finally:
        conn.close()


def ejecutar_sentencia(sql, parametros=None, cfg=None):
    """Ejecuta un INSERT/UPDATE/DELETE y devuelve las filas afectadas.
    Uso principal: preparar y limpiar datos en las pruebas."""
    conn = conectar(cfg)
    try:
        with conn.cursor() as cur:
            cur.execute(sql, parametros)
            filas = cur.rowcount
        conn.commit()
        return filas
    except psycopg2.Error as e:
        conn.rollback()
        raise ErrorOperacion(_mensaje_operacion(e)) from e
    finally:
        conn.close()


def probar_conexion(cfg=None):
    """
    Verifica la conexion y el estado de la base. Devuelve un dict con:
    version, base, usuario, tablas, indices y filas_persona.
    Lanza ErrorConexion si algo falla.
    """
    cfg = cfg or leer_configuracion()
    conn = conectar(cfg)
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT version(), current_database(), current_user")
            version, base, usuario = cur.fetchone()
            cur.execute(
                "SELECT count(*) FROM information_schema.tables "
                "WHERE table_schema = 'public' AND table_type = 'BASE TABLE'"
            )
            tablas = cur.fetchone()[0]
            cur.execute(
                "SELECT count(*) FROM pg_indexes "
                "WHERE schemaname = 'public' AND indexname LIKE 'idx\\_%'"
            )
            indices = cur.fetchone()[0]
            filas_persona = None
            if tablas:
                cur.execute("SELECT count(*) FROM persona")
                filas_persona = cur.fetchone()[0]
        return {"version": version.split(",")[0], "base": base, "usuario": usuario,
                "tablas": tablas, "indices": indices, "filas_persona": filas_persona}
    except psycopg2.Error as e:
        raise ErrorConexion("La conexion abrio, pero fallo la verificacion: "
                            + str(e).strip()) from e
    finally:
        conn.close()
