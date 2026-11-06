"""
Acceso nativo a PostgreSQL con psycopg2 
"""
import configparser
import os
import sys

import psycopg2

CLAVES_OBLIGATORIAS = ("host", "port", "dbname", "user", "password")


class ErrorConexion(Exception):
    """Error de conexion o de configuracion con mensaje listo para mostrar."""


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


def _explicar(mensaje):
    """Traduce los errores mas comunes a un mensaje entendible."""
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


def ejecutar_consulta(sql, parametros=None, cfg=None):
    """Ejecuta un SELECT y devuelve (nombres_de_columnas, filas)."""
    conn = conectar(cfg)
    try:
        with conn.cursor() as cur:
            cur.execute(sql, parametros)
            columnas = [d[0] for d in cur.description]
            return columnas, cur.fetchall()
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
