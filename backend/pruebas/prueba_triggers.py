"""
Demuestra que cada uno de los 5 triggers se dispara.
Uso:  python backend/pruebas/prueba_triggers.py
"""
import time
from datetime import date

import psycopg2

from _comun import (COD, COORD, D_HIS, D_INV, D_PAT, PAT, escalar, esperar_error, historico,
                    investigadores, limpiar, paso, patentes, probar, terminar)
from src.db.conexion import conectar, ejecutar_sentencia


def trg_normalizar():
    print("\n--- A.1 trg_investigador_normalizar (INSERT/UPDATE) ---")
    probar("Registrar investigador con correo en mayusculas", investigadores.registrar, D_INV, COORD)
    paso(investigadores.obtener(COD)["correo"] == "test.prueba@ucsm.edu.pe",
         "INSERT: el correo se guardo en minusculas")
    ejecutar_sentencia("UPDATE investigador SET escuela_profesional = %s, correo_elec = %s "
                       "WHERE codigo_ucsm = %s", ("   Escuela Test   ", "  MAYUS@UCSM.EDU.PE  ", COD))
    f = investigadores.obtener(COD)
    paso(f["escuela"] == "Escuela Test" and f["correo"] == "mayus@ucsm.edu.pe",
         "UPDATE directo: se quitaron espacios y el correo quedo en minusculas")


def trg_borrar_inventor():
    print("\n--- A.2 trg_investigador_antes_borrar ---")
    probar("Registrar patente con el investigador como inventor", patentes.registrar, D_PAT, COORD)
    esperar_error("Borrar a un investigador que es inventor", investigadores.eliminar, COD,
                  contiene="inventor")
    paso(investigadores.obtener(COD) is not None, "El investigador sigue existiendo (se revirtio)")


def trg_borrar_patente():
    print("\n--- A.4 trg_patente_antes_borrar ---")
    formato = escalar("SELECT n_formato_pat FROM formato_patente WHERE n_patente = %s", (PAT,))
    probar("Eliminar la patente (sp_eliminar_patente)", patentes.eliminar, PAT)
    restos = sum(escalar(f"SELECT COUNT(*) FROM {t} WHERE n_formato_pat = %s", (formato,))
                 for t in ("formato_patente", "formato_paten_inventores", "formato_paten_ocde",
                           "formato_patente_investigador"))
    paso(restos == 0, "Se eliminaron su formato, inventores, OCDE y vinculos")


def trg_borrar_investigador():
    print("\n--- A.2 (cascada) borrar investigador limpia su formato ---")
    formato = escalar("SELECT n_formato_inv FROM formato_investigador WHERE codigo_ucsm = %s", (COD,))
    probar("Eliminar investigador (ya sin patentes)", investigadores.eliminar, COD)
    restos = sum(escalar(f"SELECT COUNT(*) FROM {t} WHERE n_formato_inv = %s", (formato,))
                 for t in ("formato_investigador", "formato_inv_ods", "formato_inv_intereses"))
    paso(restos == 0, "Se eliminaron su formato, ODS e intereses")


def trg_patente_requiere_inventor():
    print("\n--- A.3 trg_patente_requiere_inventor (diferido, al hacer commit) ---")
    conn = conectar()
    try:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO patente (n_patente, titulo_patente, editorial, fecha_registro, "
                        "cip, pais) VALUES ('PE-9990009', 'Sin inventor', 'INDECOPI', '2025-01-01', "
                        "'A01B 1/00', 'Peru')")
            cur.execute("INSERT INTO formato_patente (n_patente, codigo_ucsm_coordinador) "
                        "VALUES ('PE-9990009', %s)", (COORD,))
        try:
            conn.commit()
            paso(False, "El commit debio fallar: una patente sin inventor no es valida")
        except psycopg2.Error as e:
            conn.rollback()
            mensaje = getattr(e.diag, "message_primary", None) or str(e)
            paso("al menos un inventor" in mensaje, f"El commit fue rechazado: {mensaje}")
    finally:
        conn.close()
    paso(escalar("SELECT COUNT(*) FROM patente WHERE n_patente = 'PE-9990009'") == 0,
         "No quedo ningun dato de la patente rechazada")


def trg_synced_at():
    print("\n--- A.5 trg_historico_synced_at ---")
    ok, uid = probar("Cargar publicacion", historico.guardar, D_HIS, COORD,
                     fecha_reporte=date(2000, 1, 1))
    if not ok:
        return
    antes = historico.obtener(uid)["synced_at"]
    time.sleep(0.1)
    probar("Modificar la publicacion", historico.guardar, {**D_HIS, "pages": "1-11"}, COORD,
           uuid_existente=uid)
    despues = historico.obtener(uid)["synced_at"]
    paso(despues > antes, f"synced_at se actualizo solo ({antes:%H:%M:%S.%f} -> {despues:%H:%M:%S.%f})")


def main():
    print("=== Prueba de triggers ===")
    limpiar()
    try:
        trg_normalizar()
        trg_borrar_inventor()
        trg_borrar_patente()
        trg_borrar_investigador()
        trg_patente_requiere_inventor()
        trg_synced_at()
    finally:
        limpiar()
    return terminar()


if __name__ == "__main__":
    import sys
    sys.exit(main())
