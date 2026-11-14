"""
Prueba del inicio de sesion del coordinador (pagina de inicio).
Uso:  python backend/pruebas/prueba_login.py
Requiere haber ejecutado instalar_bd.py (carga las contrasenias de ejemplo).
"""
from _comun import (COD_RET, COORD, DNI_RET, escalar, esperar_error, limpiar, paso, probar,
                    terminar)
from src.db.conexion import ejecutar_sentencia
from src.repositorios import coordinadores
from src.seguridad import generar_hash


def main():
    print("=== Prueba de login del coordinador ===")
    limpiar()
    try:
        ok, c = probar("Login correcto: jangulo@ucsm.edu.pe",
                       coordinadores.autenticar, "jangulo@ucsm.edu.pe", "Angulo2026!")
        if ok:
            paso(c["codigo_ucsm"] == COORD and "Angulo" in c["nombre"] and "contrasenia" not in c,
                 f"Devuelve los datos del coordinador sin la contrasenia ({c['nombre']})")
            paso(c["funcion"] == "Coordinador de repositorios",
                 f"Funcion registrada: {c['funcion']}")
        probar("Login sin distinguir mayusculas en el correo",
               coordinadores.autenticar, "JANGULO@UCSM.EDU.PE", "Angulo2026!")
        esperar_error("Contrasenia incorrecta", coordinadores.autenticar,
                      "jangulo@ucsm.edu.pe", "mala", contiene="incorrectos")
        esperar_error("La contrasenia distingue mayusculas", coordinadores.autenticar,
                      "jangulo@ucsm.edu.pe", "angulo2026!", contiene="incorrectos")
        esperar_error("Correo inexistente", coordinadores.autenticar,
                      "nadie@ucsm.edu.pe", "Angulo2026!", contiene="incorrectos")
        esperar_error("Campos vacios", coordinadores.autenticar, "", "", contiene="ingrese")

        # Coordinador retirado: con la clave correcta igual no puede entrar
        ejecutar_sentencia(
            "INSERT INTO persona (dni, nombres, apellido_paterno, apellido_materno, genero, "
            "fecha_nacimiento) VALUES (%s, 'Retirado', 'Prueba', 'Test', 'Masculino', '1980-01-01')",
            (DNI_RET,))
        ejecutar_sentencia(
            "INSERT INTO coordinador_repositorios (codigo_ucsm, dni, fecha_ocupacion_puesto, "
            "correo_electronico, contrasenia, fecha_retiro, funcion, direccion_adscrita) "
            "VALUES (%s, %s, '2024-01-01', 'retirado.prueba@ucsm.edu.pe', %s, '2025-01-01', "
            "'Prueba', 'Prueba')", (COD_RET, DNI_RET, generar_hash("Retirado1!")))
        esperar_error("Coordinador retirado no puede ingresar", coordinadores.autenticar,
                      "retirado.prueba@ucsm.edu.pe", "Retirado1!", contiene="retirado")

        paso(escalar("SELECT COUNT(*) FROM coordinador_repositorios WHERE fecha_retiro IS NULL") == 1,
             "Hay un unico coordinador en funciones (Javier Fernando Angulo Osorio)")
        ok, r = probar("Resumen para la pagina de inicio", coordinadores.resumen, COORD)
        if ok:
            paso(all(isinstance(r[k], int) for k in
                     ("investigadores", "patentes", "publicaciones", "reportes", "mis_reportes")),
                 f"Conteos: {r}")
    finally:
        limpiar()
    return terminar()


if __name__ == "__main__":
    import sys
    sys.exit(main())
    