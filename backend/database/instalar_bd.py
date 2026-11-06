"""
Crea las 27 tablas y carga los datos de ejemplo ejecutando el script SQL
con el mismo modulo de conexion del aplicativo.
Requisito: la base de datos repositorios_ucsm ya debe existir.
Uso:  python backend/database/instalar_bd.py o py backend/database/instalar_bd.py
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.db.conexion import ErrorConexion, conectar

SCRIPT = os.path.join(os.path.dirname(__file__), "base_datos_repositorio.sql")


def main():
    try:
        conn = conectar()
    except ErrorConexion as e:
        print("[FALLO]", e)
        return 1
    try:
        conn.autocommit = True          # el script ya trae sus propios BEGIN/COMMIT
        with open(SCRIPT, encoding="utf-8") as f, conn.cursor() as cur:
            cur.execute(f.read())
        print("[OK] Script ejecutado: tablas, indices y datos de ejemplo creados.")
        return 0
    except Exception as e:
        print("[FALLO] No se pudo ejecutar el script:", e)
        return 1
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
