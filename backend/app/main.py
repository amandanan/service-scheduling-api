import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from app.database.session import Base, engine

load_dotenv()

from app.models.user import User
from app.models.client import Client
from app.models.service import Service
from app.models.appointment import Appointment

from app.routes import (
    auth,
    client,
    service,
    appointment,
)

app = FastAPI(
    redirect_slashes=False
)

cors_origins = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173",
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)


app.include_router(auth.router)
app.include_router(client.router)
app.include_router(service.router)
app.include_router(appointment.router)