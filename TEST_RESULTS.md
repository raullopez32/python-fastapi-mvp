# Configuración de base de datos y aislamiento de pruebas

Fecha: 2026-10-27.
Rama: `fix/database-config-test-isolation`.

## Cambios

- `app/db.py` obtiene la URL exclusivamente de `settings.DATABASE_URL`.
  Se conserva el valor predeterminado de SQLite definido en `Settings` y la
  prioridad de las variables de entorno sobre `.env`.
- La aplicación se importa en las pruebas después de forzar `DATABASE_URL=sqlite://`.
  La creación de tablas durante la importación queda confinada a memoria.
- Cada prueba que utiliza el cliente recibe una base SQLite en memoria nueva,
  compartida entre sus sesiones mediante `StaticPool`. Al finalizar se restauran
  las dependencias y se desecha el motor, incluso si falla la prueba.
- Una barrera de SQLAlchemy rechaza conexiones a bases distintas de SQLite en
  memoria antes de invocar al controlador.
- No se modifican endpoints ni dependencias.

## Casos de prueba

1. El motor utiliza `settings.DATABASE_URL`.
2. La barrera impide crear una base SQLite en disco.
3. `DATABASE_URL` se carga desde un archivo `.env` temporal sin abrir una conexión.
4. Una variable de entorno tiene prioridad sobre ese archivo.
5. El cliente escribe únicamente en su base en memoria; se deja un registro para
   comprobar que la siguiente prueba recibe una base vacía.
6. El flujo existente de creación, consulta y eliminación utiliza la fixture aislada.

## Ejecución

Entorno autorizado fuera del repositorio:
`%TEMP%\fastapi-mvp-test-isolation\venv`, con CPython 3.12.16 y las dependencias
de `requirements.txt`. No se modificó ese archivo ni se creó un entorno dentro
del proyecto.

Desde la raíz del repositorio, en PowerShell:

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = '1'
& "$env:TEMP\fastapi-mvp-test-isolation\venv\Scripts\python.exe" -m pytest -q -p no:cacheprovider
```

Resultado final: **6 passed, 1 warning in 0.19s**, código de salida 0.

La primera ejecución produjo 5 pruebas correctas y un fallo en la comprobación
añadida de `PRAGMA database_list`, porque SQLite devuelve también esquemas
auxiliares. Se corrigió para comprobar que existe `main` y que ninguna fila
apunta a un archivo; después se ejecutó nuevamente toda la suite.

La advertencia es una deprecación de `anyio.abc.BlockingPortal` utilizada por
Starlette. No se cambiaron dependencias para resolverla, por quedar fuera del
alcance solicitado.

Las conexiones de las pruebas quedaron limitadas a SQLite en memoria. No se
inició PostgreSQL, no se importó la aplicación fuera de la fixture protegida y
no se creó `app.db`.

Comprobación estática: `git diff --check` completada sin errores.
