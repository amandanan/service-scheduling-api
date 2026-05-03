from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database.base import Base
from app.database.session import engine

# Importar models (para criar tabelas)
from app.models.client import Client
from app.models.service import Service
from app.models.appointment import Appointment
from app.models.user import User

# Importar rotas
from app.routes import client, service, appointment, auth

app = FastAPI(title="Service Scheduling API")

# ✅ CORS (ESSENCIAL para o frontend funcionar)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # front do Vite
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar rotas
app.include_router(client.router)
app.include_router(service.router)
app.include_router(appointment.router)
app.include_router(auth.router)

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"status": "API rodando"}