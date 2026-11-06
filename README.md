# Repositorios UCSM - Aplicativo (avance 30 %: conexion a la base de datos)

Aplicativo en Python que consume PostgreSQL 16 **sin frameworks ni ORM**: el SQL se escribe a mano
y se envia con `psycopg2`, un controlador (driver) que solo transporta las sentencias.

## Estructura
```
repositorios_ucsm/
  backend/
    config.ini.example       Plantilla de datos de conexion (copiar a config.ini)
    requirements.txt         Dependencias (solo psycopg2-binary)
    database/
      base_datos_repositorio.sql Script de la base (27 tablas, indices, datos de prueba)
      instalar_bd.py            Ejecuta el script desde Python
    pruebas/
      prueba_conexion.py        Prueba por consola (evidencia del avance)
    src/db/conexion.py          Lectura de config, conexion, consultas, prueba de conexion
  fronted/
    main.py                     Ventana inicial (Tkinter) con "Probar conexion"
```

## Puesta en marcha
1. Instalar Python 3.10 o superior y PostgreSQL 16.
2. Crear la base: `CREATE DATABASE repositorios_ucsm;` (pgAdmin o psql).
3. `pip install -r backend/requirements.txt`
4. Copiar `backend/config.ini.example` como `backend/config.ini` y escribir usuario y contrasenia.
5. `python backend/database/instalar_bd.py`   (crea tablas y datos de prueba)
6. `python backend/pruebas/prueba_conexion.py` (debe terminar en TODO CORRECTO)
7. `python -m fronted.main`                   (ventana con boton "Probar conexion")

En Linux, Tkinter puede requerir `sudo apt install python3-tk`.
La contrasenia tambien puede darse con la variable de entorno `UCSM_DB_PASSWORD`.
