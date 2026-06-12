import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

load_dotenv()

from app.models.user import User
from app.models.client import Client
from app.models.service import Service
from app.models.appointment import Appointment
from app.models.professional import Professional
from app.models.working_hours import WorkingHours
from app.models.package import Package, ClientPackage
from app.models.review import Review

from app.core.rate_limit import limiter

from app.routes import (
    auth,
    client,
    service,
    appointment,
    professional,
    public,
    manage,
    package,
    review,
    dashboard,
)

app = FastAPI(
    redirect_slashes=False
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

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


app.include_router(auth.router)
app.include_router(client.router)
app.include_router(service.router)
app.include_router(appointment.router)
app.include_router(professional.router)
app.include_router(public.router)
app.include_router(manage.router)
app.include_router(package.router)
app.include_router(review.router)
app.include_router(dashboard.router)