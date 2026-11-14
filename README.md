# Repositorios UCSM – Registro de investigadores y seguimiento de repositorios

Aplicativo de escritorio en **Python + PostgreSQL 16**, **sin frameworks ni ORM**:
interfaz con Tkinter (incluido en Python) y acceso a datos con `psycopg2` (solo un
controlador: envía el SQL tal cual y devuelve filas).

El coordinador de repositorios (Javier Fernando Angulo Osorio) valida los formatos de
investigador y de patente, procesa el histórico de publicaciones y genera el reporte
(Dashboard), tal como se describe en el informe.

## Estructura

```
backend/
  config.ini.example           plantilla de conexión (el config.ini real NO se sube)
  requirements.txt             única dependencia: psycopg2-binary
  database/
    base_datos_repositorio.sql reinicia e instala: 27 tablas, índices, triggers, procedimientos y datos
    instalar_bd.py             ejecuta el script anterior
  src/
    seguridad.py               hash PBKDF2 de contraseñas (librería estándar)
    db/conexion.py             conexión, consultas, CALL a procedimientos, errores legibles
    repositorios/              una capa por entidad: investigadores, patentes, historico,
                               reportes, coordinadores (+ catálogo de las 15 consultas)
  pruebas/                     prueba_conexion, prueba_login, prueba_crud,
                               prueba_triggers, prueba_reportes
frontend/
  main.py                      Login -> ventana principal
  estilos.py                   tema visual (paleta, tipografía, estilos ttk)
  vistas/                      login, inicio, investigadores, patentes, historico, reportes
```

La interfaz **nunca habla directo con la base**: llama a `backend/src/repositorios`, y
este usa `conexion.py`. Insertar, modificar y borrar se hace **solo con procedimientos
almacenados** (`CALL sp_...`).

## Puesta en marcha

1. Instalar Python 3.10+ y PostgreSQL 16.
2. Crear la base: `CREATE DATABASE repositorios_ucsm ENCODING 'UTF8';`
3. `pip install -r backend/requirements.txt`
4. Copiar `backend/config.ini.example` como `backend/config.ini` y completar los datos
   (o definir la variable de entorno `UCSM_DB_PASSWORD`).
5. Instalar la base (se puede repetir; **borra y recrea las tablas**):
   `python backend/database/instalar_bd.py`
6. Ejecutar las pruebas (ver abajo).
7. Abrir el aplicativo, **desde la raíz del repositorio**: `python -m frontend.main`

### Coordinador de repositorios (solo para demostración)

| Correo | Contraseña |
|---|---|
| jangulo@ucsm.edu.pe | Angulo2026! |

## Qué incluye el aplicativo

- **Login** del coordinador (contraseña con hash PBKDF2; un coordinador retirado no ingresa)
  y botón para probar la conexión.
- **Inicio:** datos del coordinador y Dashboard con los indicadores del repositorio
  (investigadores, escuelas, publicaciones, patentes, ODS vinculados, ranking de ODS y
  escuelas con más investigadores).
- **Investigadores / Patentes / Histórico:** listado y formulario para registrar,
  modificar y eliminar. Los errores de la base (CHECK, triggers, procedimientos) se
  muestran con mensajes claros.
- **Reportes:** 15 consultas (7 con JOIN) y generación del reporte con `sp_generar_reporte`.

## Base de datos

27 tablas · 21 índices secundarios · 5 triggers · 9 procedimientos.

| Procedimiento | Operación |
|---|---|
| `sp_registrar_investigador`, `sp_modificar_investigador`, `sp_eliminar_investigador` | Formato de investigador |
| `sp_registrar_patente`, `sp_modificar_patente`, `sp_eliminar_patente` | Formato de patente |
| `sp_cargar_historico`, `sp_eliminar_historico` | Histórico de publicaciones |
| `sp_generar_reporte` | Reporte (Dashboard) |

| Trigger | Qué hace |
|---|---|
| `trg_investigador_normalizar` | correo en minúsculas y sin espacios (INSERT/UPDATE) |
| `trg_investigador_antes_borrar` | impide borrar a un inventor y limpia su formato |
| `trg_patente_requiere_inventor` | toda patente debe tener inventor (se valida al hacer commit) |
| `trg_patente_antes_borrar` | al borrar la patente se elimina su formato |
| `trg_historico_synced_at` | cada actualización refresca `synced_at` |

## Pruebas (cada una termina en `TODO CORRECTO` o `HAY ... FALLIDAS`)

```
python backend/pruebas/prueba_conexion.py ó py backend/pruebas/prueba_conexion.py  conexión, 27 tablas, 21 índices
python backend/pruebas/prueba_login.py ó  py backend/pruebas/prueba_login.py    login correcto, clave errónea, coordinador retirado
python backend/pruebas/prueba_crud.py ó   py backend/pruebas/prueba_crud.py    alta, modificación y baja con procedimientos + casos rechazados
python backend/pruebas/prueba_triggers.py ó py backend/pruebas/prueba_triggers.py   cada uno de los 5 triggers disparándose
python backend/pruebas/prueba_reportes.py ó  py backend/pruebas/prueba_reportes.py   15 consultas (≥10, ≥6 con JOIN) y sp_generar_reporte
```

Las pruebas crean datos ficticios (códigos 2099…, DNI 99999…) y los borran al terminar.

## Notas

- Un investigador que aparece en un reporte generado (`total_investigadores`) no se puede
  eliminar: es una restricción de integridad histórica. Para demostrar la baja, registre un
  investigador nuevo y elimínelo antes de generar reportes.
- Los datos de conexión y contraseñas reales no se suben a GitHub (`.gitignore`).
