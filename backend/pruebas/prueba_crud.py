"""
Prueba de los CRUD (insertar, modificar, borrar) de investigadores, patentes y
publicaciones, todos mediante procedimientos almacenados. Incluye casos que la
base debe rechazar. Crea datos ficticios y los borra al terminar.
Uso:  python backend/pruebas/prueba_crud.py
"""
from datetime import date

from _comun import (COD, COORD, D_HIS, D_INV, D_PAT, ODS, PAT, TITULO_HIS, esperar_error,
                    escalar, investigadores, historico, limpiar, paso, patentes, probar, terminar)


def crud_investigador():
    print("\n--- Investigador ---")
    probar("Registrar investigador (sp_registrar_investigador)", investigadores.registrar, D_INV, COORD)
    f = investigadores.obtener(COD)
    paso(bool(f) and f["nombres"] == "Prueba" and f["ods"] == [ODS[8]],
         "Consultar: los datos guardados coinciden")
    esperar_error("Registrar al mismo investigador otra vez", investigadores.registrar, D_INV, COORD,
                  contiene="ya esta registrado")
    otro = {**D_INV, "dni": "99999903", "codigo_ucsm": 2099000003, "orcid": "0000-0009-9999-9993",
            "scopus_id": 9900000003, "link_cti": "https://ctivitae.concytec.gob.pe/x/99999903"}
    esperar_error("Registrar con celular invalido (CHECK)", investigadores.registrar,
                  {**otro, "celular": 123456789}, COORD, contiene="celular")
    esperar_error("Registrar con coordinador inexistente", investigadores.registrar, otro, 1099999999,
                  contiene="coordinador")
    esperar_error("Registrar con DNI no numerico", investigadores.registrar,
                  {**otro, "dni": "ABC12345"}, COORD, contiene="dni")
    paso(escalar("SELECT COUNT(*) FROM persona WHERE dni = '99999903'") == 0,
         "Un registro rechazado no deja datos a medias (rollback)")

    cambios = {**D_INV, "escuela": "Ingeniería Civil", "celular": 988111222,
               "ods": [ODS[3], ODS[11]], "intereses": "Pruebas, Calidad"}
    probar("Modificar investigador (sp_modificar_investigador)", investigadores.modificar, COD, cambios)
    f = investigadores.obtener(COD)
    paso(f["escuela"] == "Ingeniería Civil" and f["celular"] == 988111222
         and sorted(f["ods"]) == sorted([ODS[3], ODS[11]]) and "Calidad" in f["intereses"],
         "Consultar: los cambios quedaron guardados")
    esperar_error("Modificar un investigador inexistente", investigadores.modificar, 2099999999,
                  cambios, contiene="no existe")
    paso(any(fila[0] == COD for fila in investigadores.listar("Automatica")),
         "Listar con filtro encuentra al investigador")


def crud_patente():
    print("\n--- Patente ---")
    probar("Registrar patente (sp_registrar_patente)", patentes.registrar, D_PAT, COORD)
    f = patentes.obtener(PAT)
    paso(bool(f) and f["inventores"] == [COD] and "Ingeniería y tecnología" in f["ocde"],
         "Consultar: inventor y clasificacion OCDE guardados")
    esperar_error("Registrar con inventor inexistente", patentes.registrar,
                  {**D_PAT, "n_patente": "PE-9990002", "inventores": [2099999999]}, COORD,
                  contiene="inventores")
    esperar_error("Registrar sin inventores", patentes.registrar,
                  {**D_PAT, "n_patente": "PE-9990002", "inventores": []}, COORD,
                  contiene="al menos un inventor")
    esperar_error("Registrar con numero de patente invalido (CHECK)", patentes.registrar,
                  {**D_PAT, "n_patente": "ABC"}, COORD, contiene="formato PE-")
    esperar_error("Registrar la misma patente dos veces", patentes.registrar, D_PAT, COORD,
                  contiene="ya esta registrada")

    cambios = {**D_PAT, "titulo": "Patente de prueba (modificada)", "pais": "Chile",
               "ocde": "Ciencias naturales | Matematicas\nIngeniería y tecnología | Otros"}
    probar("Modificar patente (sp_modificar_patente)", patentes.modificar, PAT, cambios)
    f = patentes.obtener(PAT)
    paso(f["titulo"].endswith("(modificada)") and f["pais"] == "Chile" and f["ocde"].count("|") == 2,
         "Consultar: titulo, pais y 2 lineas OCDE actualizados")
    esperar_error("Modificar quitando todos los inventores", patentes.modificar, PAT,
                  {**cambios, "inventores": []}, contiene="al menos un inventor")
    esperar_error("Modificar una patente inexistente", patentes.modificar, "PE-9999999", cambios,
                  contiene="no existe")
    esperar_error("Eliminar una patente inexistente", patentes.eliminar, "PE-9999999",
                  contiene="no existe")
    probar("Eliminar patente (sp_eliminar_patente)", patentes.eliminar, PAT)
    paso(patentes.obtener(PAT) is None, "La patente ya no existe")


def crud_historico():
    print("\n--- Publicacion (historico) ---")
    ok, uid = probar("Cargar publicacion nueva (sp_cargar_historico)", historico.guardar, D_HIS, COORD,
                     fecha_reporte=date(2000, 1, 1))
    if not ok:
        return
    f = historico.obtener(uid)
    paso(bool(f) and f["title"] == TITULO_HIS and len(f["version"]) == 40
         and f["total_number_of_contributors"] == 1, "Consultar: datos y hash de version correctos")
    cambios = {**D_HIS, "title": TITULO_HIS + " (modificada)", "contributors": "Uno, Autor\nDos, Autor"}
    probar("Modificar publicacion (mismo UUID, sp_cargar_historico)", historico.guardar, cambios, COORD,
           uuid_existente=uid)
    f = historico.obtener(uid)
    paso(f["title"].endswith("(modificada)") and f["total_number_of_contributors"] == 2
         and len(f["contributors"]) == 2, "Consultar: titulo y 2 contribuyentes actualizados")
    paso(escalar("SELECT COUNT(*) FROM historico WHERE uuid = %s::uuid", (uid,)) == 1,
         "Modificar no duplica el registro")
    esperar_error("Cargar sin contribuyentes", historico.guardar, {**D_HIS, "contributors": ""}, COORD,
                  contiene="contribuyente", fecha_reporte=date(2000, 1, 1))
    esperar_error("Cargar con URL invalida (CHECK)", historico.guardar,
                  {**D_HIS, "portal_url": "ftp://x"}, COORD, contiene="URL", fecha_reporte=date(2000, 1, 1))
    probar("Eliminar publicacion (sp_eliminar_historico)", historico.eliminar, uid)
    paso(historico.obtener(uid) is None, "La publicacion ya no existe")
    esperar_error("Eliminar una publicacion inexistente", historico.eliminar, uid, contiene="no existe")


def eliminar_investigador():
    print("\n--- Investigador (baja) ---")
    esperar_error("Eliminar un investigador inexistente", investigadores.eliminar, 2099999999,
                  contiene="no existe")
    probar("Eliminar investigador (sp_eliminar_investigador)", investigadores.eliminar, COD)
    paso(investigadores.obtener(COD) is None, "El investigador ya no existe")
    paso(escalar("SELECT COUNT(*) FROM persona WHERE dni = '99999901'") == 0,
         "Tambien se elimino su registro de persona")


def main():
    print("=== Prueba de CRUD con procedimientos almacenados ===")
    limpiar()
    try:
        crud_investigador()
        crud_patente()
        crud_historico()
        eliminar_investigador()
    finally:
        limpiar()
    return terminar()


if __name__ == "__main__":
    import sys
    sys.exit(main())
