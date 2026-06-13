import os

from contextlib import asynccontextmanager

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
from app.models.review import Review
from app.models.time_block import TimeBlock

from app.core.rate_limit import limiter
from app.core.reminders import (
    start_reminder_scheduler,
    stop_reminder_scheduler,
)

from app.routes import (
    auth,
    client,
    service,
    appointment,
    professional,
    public,
    manage,
    review,
    dashboard,
    settings,
    time_block,
    staff,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Optional in-process reminder loop (enabled via REMINDERS_ENABLED).
    start_reminder_scheduler()
    yield
    stop_reminder_scheduler()


app = FastAPI(
    redirect_slashes=False,
    lifespan=lifespan,
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


@app.get("/health", tags=["Health"])
def health():
    """Liveness probe for load balancers and container orchestrators."""
    return {"status": "ok"}


app.include_router(auth.router)
app.include_router(client.router)
app.include_router(service.router)
app.include_router(appointment.router)
app.include_router(professional.router)
app.include_router(public.router)
app.include_router(manage.router)
app.include_router(review.router)
app.include_router(dashboard.router)
app.include_router(settings.router)
app.include_router(time_block.router)
app.include_router(staff.router)