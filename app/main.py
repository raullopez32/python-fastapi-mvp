from fastapi import FastAPI
from .routers import items
from .db import Base, engine

app = FastAPI(title="MVP FastAPI", version="0.2.0")

Base.metadata.create_all(bind=engine)

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(items.router)
