import asyncio
from datetime import date

from fastapi import APIRouter, Depends
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.database.session import SessionLocal

from app.models.user import User

from app.schemas.dashboard import DashboardStats, DashboardMetrics

from app.core.account import get_account_owner, require_management
from app.core.dashboard_data import compute_stats, compute_metrics
from app.core.report.pdf import generate_pdf, generate_csv

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


# DB
def get_db():
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


@router.get("/stats", response_model=DashboardStats)
def get_dashboard_stats(
    professional_id: int | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    db: Session = Depends(get_db),
    account_owner: User = Depends(get_account_owner),
    _: User = Depends(require_management),
):
    return compute_stats(db, account_owner, professional_id, start_date, end_date)


@router.get("/metrics", response_model=DashboardMetrics)
def get_dashboard_metrics(
    start_date: date | None = None,
    end_date: date | None = None,
    db: Session = Depends(get_db),
    account_owner: User = Depends(get_account_owner),
    _: User = Depends(require_management),
):
    return compute_metrics(db, account_owner, start_date, end_date)


@router.get("/report.pdf")
async def get_report_pdf(
    start_date: date | None = None,
    end_date: date | None = None,
    db: Session = Depends(get_db),
    account_owner: User = Depends(get_account_owner),
    _: User = Depends(require_management),
):
    loop = asyncio.get_running_loop()
    pdf_bytes = await loop.run_in_executor(
        None,
        lambda: generate_pdf(db, account_owner, start_date, end_date),
    )
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="relatorio.pdf"'},
    )


@router.get("/export.csv")
def get_export_csv(
    start_date: date | None = None,
    end_date: date | None = None,
    db: Session = Depends(get_db),
    account_owner: User = Depends(get_account_owner),
    _: User = Depends(require_management),
):
    csv_text = generate_csv(db, account_owner, start_date, end_date)
    return Response(
        content=csv_text,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="dados.csv"'},
    )
