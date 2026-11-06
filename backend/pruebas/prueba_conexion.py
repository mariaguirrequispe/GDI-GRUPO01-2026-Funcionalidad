"""
Prueba de conexion por consola (evidencia para la entrega al 30 %).
Uso:  python backend/pruebas/prueba_conexion.py o py backend/pruebas/prueba_conexion.py
Devuelve codigo 0 si todo esta correcto y 1 si algo falla.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.db.conexion import ErrorConexion, ejecutar_consulta, leer_configuracion, probar_conexion

TABLAS_ESPERADAS = 27
INDICES_ESPERADOS = 21


def paso(ok, texto):
    print(("[OK]    " if ok else "[FALLO] ") + texto)
    return ok


def main():
    print("=== Prueba de conexion - Repositorios UCSM ===")
    try:
        cfg = leer_configuracion()
        paso(True, f"config.ini leido ({cfg['user']}@{cfg['host']}:{cfg['port']}/{cfg['dbname']})")
        info = probar_conexion(cfg)
    except ErrorConexion as e:
        paso(False, str(e))
        return 1

    resultados = [
        paso(True, f"Conexion establecida - {info['version']}"),
        paso(True, f"Base: {info['base']} | Usuario: {info['usuario']}"),
        paso(info["tablas"] == TABLAS_ESPERADAS,
             f"Tablas en el esquema public: {info['tablas']} (esperadas {TABLAS_ESPERADAS})"),
        paso(info["indices"] == INDICES_ESPERADOS,
             f"Indices secundarios idx_*: {info['indices']} (esperados {INDICES_ESPERADOS})"),
    ]

    # Consulta con JOIN y parametro: demuestra que el aplicativo consume la base.
    try:
        columnas, filas = ejecutar_consulta(
            "SELECT i.codigo_ucsm, p.apellido_paterno, p.nombres, i.escuela_profesional "
            "FROM investigador i JOIN persona p ON p.dni = i.dni "
            "WHERE i.escuela_profesional ILIKE %s ORDER BY p.apellido_paterno",
            ("%Ingenier%",), cfg)
    except Exception as e:
        resultados.append(paso(False, "Consulta con JOIN: " + str(e).splitlines()[0]))
    else:
        resultados.append(paso(len(filas) > 0, f"Consulta con JOIN: {len(filas)} fila(s)"))
        for f in filas:
            print("          ", dict(zip(columnas, f)))

    print("RESULTADO:", "TODO CORRECTO" if all(resultados) else "HAY PRUEBAS FALLIDAS")
    return 0 if all(resultados) else 1


if __name__ == "__main__":
    sys.exit(main())
