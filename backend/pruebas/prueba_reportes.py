"""
Prueba de los reportes: ejecuta las 15 consultas  y
el procedimiento sp_generar_reporte.
Uso:  python backend/pruebas/prueba_reportes.py
"""
from datetime import date

from _comun import COORD, ErrorConexion, escalar, limpiar, paso, probar, terminar
from backend.src import reportes
from src.repositorios.catalogo_reportes import CONSULTAS

FECHA = date(2000, 1, 1)
WHERE = "WHERE dia = 1 AND mes = 1 AND anio = 2000"


def consultas():
    print("\n--- Consultas (reportes) ---")
    for id_consulta, titulo, usa_join in reportes.catalogo():
        marca = "[JOIN] " if usa_join else "       "
        try:
            _, columnas, filas = reportes.ejecutar(id_consulta)
        except ErrorConexion as e:
            paso(False, f"Consulta {id_consulta:02d} {titulo}: {e}")
            continue
        paso(len(filas) > 0, f"Consulta {id_consulta:02d} {marca}{titulo}: {len(filas)} fila(s)")
    con_join = sum("JOIN" in c["sql"].upper() for c in CONSULTAS)
    paso(len(CONSULTAS) >= 10, f"Hay {len(CONSULTAS)} reportes (requisito: al menos 10)")
    paso(con_join >= 6, f"{con_join} reportes usan JOIN (requisito: al menos 6)")


def generar():
    print("\n--- sp_generar_reporte ---")
    probar("Generar el reporte del 01/01/2000", reportes.generar, FECHA, COORD)
    probar("Generarlo otra vez (se reemplaza, no se duplica)", reportes.generar, FECHA, COORD)
    paso(escalar("SELECT COUNT(*) FROM reporte WHERE dia = 1 AND mes = 1 AND anio = 2000") == 1,
         "Existe un unico reporte para esa fecha")
    paso(escalar(f"SELECT COUNT(*) FROM total_investigadores {WHERE}") ==
         escalar("SELECT COUNT(*) FROM investigador"), "total_investigadores coincide con investigador")
    paso(escalar(f"SELECT COUNT(*) FROM total_publicaciones {WHERE}") ==
         escalar("SELECT COUNT(DISTINCT title) FROM historico"),
         "total_publicaciones coincide con historico")
    paso(escalar(f"SELECT COUNT(*) FROM tops_escuelas {WHERE}") >= 1, "Se genero el top de escuelas")
    paso(escalar(f"SELECT COUNT(*) FROM rankings_ods {WHERE}") >= 1, "Se genero el ranking de ODS")
    texto = reportes.detalle(FECHA)
    paso("Ranking de ODS" in texto and "Distribución de ODS" in texto,
         "El detalle del reporte se arma con las 8 secciones")
    paso(any(r[0] == "2000-01-01" for r in reportes.emitidos()), "El reporte aparece en la lista de emitidos")


def main():
    print("=== Prueba de reportes ===")
    limpiar()
    try:
        consultas()
        generar()
    finally:
        limpiar()
    return terminar()


if __name__ == "__main__":
    import sys
    sys.exit(main())