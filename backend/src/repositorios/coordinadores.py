"""Coordinador de repositorios: inicio de sesion y resumen de la pagina de inicio."""
from ..db.conexion import ErrorOperacion, consultar_dicts
from ..seguridad import verificar

_SQL_LOGIN = """
SELECT c.codigo_ucsm, c.correo_electronico, c.contrasenia, c.funcion, c.direccion_adscrita,
       c.fecha_ocupacion_puesto, c.fecha_retiro,
       p.nombres, p.apellido_paterno, p.apellido_materno
FROM coordinador_repositorios c
JOIN persona p ON p.dni = c.dni
WHERE lower(c.correo_electronico) = lower(%s)
"""

_SQL_RESUMEN = """
SELECT (SELECT COUNT(*) FROM investigador)                       AS investigadores,
       (SELECT COUNT(*) FROM patente)                            AS patentes,
       (SELECT COUNT(*) FROM historico)                          AS publicaciones,
       (SELECT COUNT(*) FROM reporte)                            AS reportes,
       (SELECT COUNT(*) FROM reporte
         WHERE codigo_ucsm_coordinador = %s)                     AS mis_reportes
"""


def autenticar(correo, clave, cfg=None):
    """Devuelve los datos del coordinador (sin la contrasenia) o lanza ErrorOperacion."""
    correo = (correo or "").strip()
    if not correo or not clave:
        raise ErrorOperacion("Ingrese su correo y su contrasenia.")
    filas = consultar_dicts(_SQL_LOGIN, (correo,), cfg)
    if not filas or not verificar(clave, filas[0]["contrasenia"]):
        raise ErrorOperacion("Correo o contrasenia incorrectos.")
    coord = filas[0]
    if coord["fecha_retiro"] is not None:
        raise ErrorOperacion("Este coordinador ya fue retirado y no puede ingresar.")
    del coord["contrasenia"]
    coord["nombre"] = (f"{coord['nombres']} {coord['apellido_paterno']} "
                       f"{coord['apellido_materno']}")
    return coord


def resumen(codigo_coordinador, cfg=None):
    """Conteos para las tarjetas de la pagina de inicio."""
    return consultar_dicts(_SQL_RESUMEN, (codigo_coordinador,), cfg)[0]
