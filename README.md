# FastAPI MVP Project

Este es un proyecto mínimo hecho con **FastAPI** que expone un CRUD sencillo para manejar items.  
Incluye validación con **Pydantic v2**, documentación automática de la API, pruebas con **pytest**, y configuración para correr en **Docker / Docker Compose**.

---

## Correr localmente (Python 3.12 recomendado)

1. Clonar el repositorio e instalar dependencias:
```bash
git clone <repo-url>
cd python-fastapi-mvp

python -m venv .venv
.\.venv\Scripts\activate

pip install -r requirements.txt
```

2. Iniciar la API:
```bash
uvicorn app.main:app --reload
```

3. Revisar la documentación interactiva:
- Swagger UI → http://127.0.0.1:8000/docs  
- ReDoc → http://127.0.0.1:8000/redoc  
- Healthcheck → http://127.0.0.1:8000/health

---

## Correr con Docker

Necesitas tener **Docker Desktop** en ejecución.

1. Construir la imagen:
```bash
docker compose build
```

2. Levantar los contenedores:
```bash
docker compose up
```

La API queda disponible en:  
- Swagger UI → http://localhost:8000/docs  
- Healthcheck → http://localhost:8000/health

3. Apagar los contenedores:
```bash
docker compose down
```

4. Ejecutar pruebas dentro del contenedor:
```bash
docker compose run --rm fastapi pytest -q
```

---

## Endpoints de ejemplo

### Healthcheck
- **GET** `/health`
```json
{ "status": "ok" }
```

### Listar items
- **GET** `/items/`
```json
[]
```

### Crear un item
- **POST** `/items/`
```json
{
  "name": "Laptop",
  "price": 1200
}
```
Respuesta:
```json
{
  "id": "a4d7f0e6-4e5a-4cb2-9f54-1a98c1c0a452",
  "name": "Laptop",
  "price": 1200
}
```

### Obtener item por ID
- **GET** `/items/{id}`  
Ejemplo: `/items/a4d7f0e6-4e5a-4cb2-9f54-1a98c1c0a452`

### Borrar item
- **DELETE** `/items/{id}`  
Respuesta:
```
204 No Content
```

Puedes probar los endpoints desde **Swagger UI**, **Postman** o con `curl`:
```bash
curl -X POST http://localhost:8000/items/ -H "Content-Type: application/json" -d '{"name":"Laptop","price":1200}'
```

---

## Ejecutar pruebas
Correr los tests en local:
```bash
pytest -q
```

Resultado esperado:
```
.
1 passed in 0.50s
```

También puedes correrlos dentro del contenedor:
```bash
docker compose run --rm fastapi pytest -q
```

---

## Notas
- Actualmente los datos se almacenan en **PostgreSQL** cuando corres con Docker, o en SQLite local si no defines una base externa.  
- El proyecto está configurado en **Python 3.12**.

---

## Stack utilizado
- FastAPI  
- Pydantic v2  
- Uvicorn  
- SQLAlchemy + PostgreSQL  
- Pytest  
- Docker / Docker Compose  
