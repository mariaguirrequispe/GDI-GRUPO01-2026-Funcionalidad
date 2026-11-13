"""
Prueba del inicio de sesion del coordinador (pagina de inicio).
Uso:  python backend/pruebas/prueba_login.py
Requiere haber ejecutado instalar_bd.py (carga las contrasenias de ejemplo).
"""
from _comun import COD_RET, COORD, DNI_RET, esperar_error, limpiar, paso, probar, terminar
from src.db.conexion import ejecutar_sentencia
from backend.src import coordinadores
from src.seguridad import generar_hash


def main():
    print("=== Prueba de login del coordinador ===")
    limpiar()
    try:
        ok, c = probar("Login correcto: carlos.paredes@ucsm.edu.pe",
                       coordinadores.autenticar, "carlos.paredes@ucsm.edu.pe", "Carlos2026!")
        if ok:
            paso(c["codigo_ucsm"] == COORD and "Paredes" in c["nombre"] and "contrasenia" not in c,
                 f"Devuelve los datos del coordinador sin la contrasenia ({c['nombre']})")
        probar("Login sin distinguir mayusculas en el correo",
               coordinadores.autenticar, "CARLOS.PAREDES@UCSM.EDU.PE", "Carlos2026!")
        probar("Login correcto: luis.gomez@ucsm.edu.pe",
               coordinadores.autenticar, "luis.gomez@ucsm.edu.pe", "Luis2026!")
        esperar_error("Contrasenia incorrecta", coordinadores.autenticar,
                      "carlos.paredes@ucsm.edu.pe", "mala", contiene="incorrectos")
        esperar_error("Correo inexistente", coordinadores.autenticar,
                      "nadie@ucsm.edu.pe", "Carlos2026!", contiene="incorrectos")
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
