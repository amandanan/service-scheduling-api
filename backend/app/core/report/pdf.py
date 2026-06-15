"""PDF and CSV report generator.

generate_pdf() renders the Jinja2 template via WeasyPrint and returns PDF bytes.
generate_csv() returns CSV text of the tabular data sections.

Both functions are synchronous; the route handler wraps them with run_in_executor
so they don't block the event loop.
"""

import csv
import io
from datetime import date, datetime, timedelta
from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from sqlalchemy.orm import Session

from app.core.dashboard_data import (
    compute_hourly_distribution,
    compute_metrics,
    compute_stats,
)
from app.core.report.charts import horizontal_bars, line_chart, vertical_bars
from app.core.report.insights import build_insights
from app.models.user import User

_TEMPLATES_DIR = Path(__file__).parent.parent.parent / "templates"
_env = Environment(loader=FileSystemLoader(str(_TEMPLATES_DIR)), autoescape=True)


def _prior_period(start: date, end: date) -> tuple[date, date]:
    """Return the window immediately before start..end (same length)."""
    length = (end - start).days + 1
    prev_end = start - timedelta(days=1)
    prev_start = prev_end - timedelta(days=length - 1)
    return prev_start, prev_end


def _fmt_period(start: date, end: date) -> str:
    months = [
        "jan", "fev", "mar", "abr", "mai", "jun",
        "jul", "ago", "set", "out", "nov", "dez",
    ]
    if start.month == end.month and start.year == end.year:
        return f"{start.day}–{end.day} de {months[start.month - 1]}/{start.year}"
    return (
        f"{start.day}/{months[start.month - 1]}"
        f"–{end.day}/{months[end.month - 1]}/{end.year}"
    )


def generate_pdf(
    db: Session,
    account_owner: User,
    start_date: date | None = None,
    end_date: date | None = None,
) -> bytes:
    stats = compute_stats(db, account_owner, start_date=start_date, end_date=end_date)
    metrics = compute_metrics(db, account_owner, start_date=start_date, end_date=end_date)
    hourly = compute_hourly_distribution(
        db, account_owner, start_date=start_date, end_date=end_date
    )

    period = stats["period"]
    prev_start, prev_end = _prior_period(period["start"], period["end"])
    prev_metrics = compute_metrics(db, account_owner, start_date=prev_start, end_date=prev_end)

    insights = build_insights(stats, metrics, hourly, prev_metrics)

    kpis = stats["kpis"]
    period_days = (period["end"] - period["start"]).days + 1
    daily_capacity = account_owner.daily_capacity or 8
    period_occupancy = min(
        round(period["appointments"] / (daily_capacity * period_days) * 100), 100
    )

    charts = {
        "revenue_by_service": horizontal_bars(
            metrics["revenue_by_service"],
            label_key="service_name",
            value_key="revenue",
            money=True,
        ),
        "weekly_appointments": vertical_bars(
            stats["weekly_appointments"],
            label_key="day",
            value_key="agendamentos",
        ),
        "monthly_revenue": line_chart(
            stats["monthly_revenue_chart"],
            label_key="month",
            value_key="revenue",
        ),
        "hourly_appointments": vertical_bars(
            hourly,
            label_key="label",
            value_key="agendamentos",
        ),
    }

    template = _env.get_template("report.html")
    html_string = template.render(
        owner=account_owner,
        period=period,
        period_label=_fmt_period(period["start"], period["end"]),
        generated_at=datetime.now().strftime("%d/%m/%Y %H:%M"),
        kpis=kpis,
        metrics=metrics,
        insights=insights,
        period_occupancy=period_occupancy,
        top_services=stats["top_services"],
        top_clients=stats["top_clients"],
        inactive_clients=stats["inactive_clients"],
        inactive_total=stats["inactive_total"],
        charts=charts,
    )

    from weasyprint import HTML  # lazy: avoids loading native libs at import time

    return HTML(string=html_string).write_pdf()


def generate_csv(
    db: Session,
    account_owner: User,
    start_date: date | None = None,
    end_date: date | None = None,
) -> str:
    stats = compute_stats(db, account_owner, start_date=start_date, end_date=end_date)
    metrics = compute_metrics(db, account_owner, start_date=start_date, end_date=end_date)

    buf = io.StringIO()
    writer = csv.writer(buf)

    writer.writerow(["=== Receita por Serviço ==="])
    writer.writerow(["Serviço", "Receita (R$)", "Atendimentos"])
    for row in metrics["revenue_by_service"]:
        writer.writerow([row["service_name"], f"{row['revenue']:.2f}", row["count"]])

    writer.writerow([])
    writer.writerow(["=== Serviços Mais Solicitados ==="])
    writer.writerow(["Serviço", "Total"])
    for row in stats["top_services"]:
        writer.writerow([row["name"], row["total"]])

    writer.writerow([])
    writer.writerow(["=== Top Clientes ==="])
    writer.writerow(["Nome", "Agendamentos"])
    for row in stats["top_clients"]:
        writer.writerow([row["name"], row["total"]])

    writer.writerow([])
    writer.writerow(["=== Clientes Sem Retorno (+90 dias) ==="])
    writer.writerow(["Nome", "Dias sem retorno"])
    for row in stats["inactive_clients"]:
        writer.writerow([row["name"], row["days"]])

    return buf.getvalue()
