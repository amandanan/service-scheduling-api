from datetime import datetime, date, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import SessionLocal

from app.models.user import User
from app.models.client import Client
from app.models.service import Service
from app.models.professional import Professional
from app.models.appointment import Appointment
from app.models.review import Review

from app.schemas.dashboard import DashboardStats

from app.core.dependencies import get_current_user

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


WEEKDAYS = ["Dom", "Seg", "Ter", "Qua", "Qui", "Sex", "Sab"]

MONTHS = [
    "Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
    "Jul", "Ago", "Set", "Out", "Nov", "Dez",
]

INACTIVE_DAYS = 90


# DB
def get_db():
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


def _is_billable(appointment: Appointment) -> bool:
    # Cancellations and no-shows do not generate revenue.
    return appointment.status not in ("cancelled", "no_show")


def _brief(appointment: Appointment, clients_by_id, services_by_id, professionals_by_id):
    service = services_by_id.get(appointment.service_id)
    client = clients_by_id.get(appointment.client_id)
    professional = professionals_by_id.get(appointment.professional_id)

    return {
        "id": appointment.id,
        "client": client.full_name if client else "Cliente",
        "service": service.name if service else "Serviço",
        "professional": professional.name if professional else "Profissional",
        "scheduled_at": appointment.scheduled_at,
        "time": appointment.scheduled_at.strftime("%H:%M"),
    }


@router.get("/stats", response_model=DashboardStats)
def get_dashboard_stats(
    professional_id: int | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    monthly_goal = current_user.monthly_goal
    daily_capacity = current_user.daily_capacity

    now = datetime.now()
    today = now.date()
    tomorrow = today + timedelta(days=1)

    current_month = now.month
    current_year = now.year

    # The analytical sections (period summary, rankings, weekly chart) are
    # scoped to a date range; it defaults to the current month.
    period_start = start_date or date(current_year, current_month, 1)
    period_end = end_date or today

    def in_period(appointment: Appointment) -> bool:
        d = appointment.scheduled_at.date()
        return (
            appointment.status != "cancelled"
            and period_start <= d <= period_end
        )

    if current_month == 1:
        previous_month, previous_year = 12, current_year - 1
    else:
        previous_month, previous_year = current_month - 1, current_year

    # ---- Load the owner's data once ----
    services = db.query(Service).filter(
        Service.owner_id == current_user.id
    ).all()
    services_by_id = {s.id: s for s in services}

    clients = db.query(Client).filter(
        Client.owner_id == current_user.id
    ).all()
    clients_by_id = {c.id: c for c in clients}

    professionals = db.query(Professional).filter(
        Professional.owner_id == current_user.id
    ).all()
    professionals_by_id = {p.id: p for p in professionals}

    appointments_query = db.query(Appointment).filter(
        Appointment.owner_id == current_user.id
    )

    if professional_id is not None:
        appointments_query = appointments_query.filter(
            Appointment.professional_id == professional_id
        )

    appointments = appointments_query.all()

    def price_of(appointment: Appointment) -> float:
        service = services_by_id.get(appointment.service_id)
        return float(service.price) if service and service.price else 0.0

    # ---- Revenue windows (billable only) ----
    today_revenue = 0.0
    month_revenue = 0.0
    previous_month_revenue = 0.0
    forecast_revenue = 0.0

    today_list = []
    tomorrow_list = []

    for appointment in appointments:
        scheduled = appointment.scheduled_at
        billable = _is_billable(appointment)

        if billable:
            if scheduled.date() == today:
                today_revenue += price_of(appointment)

            if (
                scheduled.month == current_month
                and scheduled.year == current_year
            ):
                month_revenue += price_of(appointment)

            if (
                scheduled.month == previous_month
                and scheduled.year == previous_year
            ):
                previous_month_revenue += price_of(appointment)

            if scheduled >= now:
                forecast_revenue += price_of(appointment)

        # appointment lists exclude cancelled appointments
        if appointment.status != "cancelled":
            if scheduled.date() == today:
                today_list.append(appointment)
            elif scheduled.date() == tomorrow:
                tomorrow_list.append(appointment)

    today_appointments = len(today_list)

    average_ticket = (
        today_revenue / today_appointments
        if today_appointments > 0
        else 0.0
    )

    occupancy = round((today_appointments / daily_capacity) * 100)
    occupancy_rate = min(occupancy, 100)

    if previous_month_revenue > 0:
        monthly_growth = (
            (month_revenue - previous_month_revenue) / previous_month_revenue
        ) * 100
    elif month_revenue > 0:
        monthly_growth = 100.0
    else:
        monthly_growth = 0.0

    goal_progress = min((month_revenue / monthly_goal) * 100, 100) if monthly_goal else 0.0

    # ---- New clients this month ----
    new_clients_month = sum(
        1
        for c in clients
        if c.created_at
        and c.created_at.month == current_month
        and c.created_at.year == current_year
    )

    # ---- Reviews aggregate ----
    review_ratings = [
        r.rating
        for r in db.query(Review).filter(
            Review.owner_id == current_user.id
        ).all()
    ]
    total_reviews = len(review_ratings)
    average_rating = (
        round(sum(review_ratings) / total_reviews, 1)
        if total_reviews
        else None
    )

    # ---- Appointment lists (sorted) ----
    today_list.sort(key=lambda a: a.scheduled_at)
    tomorrow_list.sort(key=lambda a: a.scheduled_at)

    upcoming = sorted(
        (
            a for a in appointments
            if a.status != "cancelled" and a.scheduled_at > now
        ),
        key=lambda a: a.scheduled_at,
    )[:5]

    # ---- Period summary ----
    period_appointments = [a for a in appointments if in_period(a)]
    period_count = len(period_appointments)
    period_revenue = sum(
        price_of(a) for a in period_appointments if _is_billable(a)
    )
    period_ticket = period_revenue / period_count if period_count else 0.0

    # ---- Top services (scoped to the period) ----
    service_count = {}
    for appointment in period_appointments:
        service_count[appointment.service_id] = (
            service_count.get(appointment.service_id, 0) + 1
        )

    top_services = sorted(
        (
            {
                "name": services_by_id[sid].name if sid in services_by_id else "Serviço",
                "total": total,
            }
            for sid, total in service_count.items()
        ),
        key=lambda item: item["total"],
        reverse=True,
    )[:5]

    # ---- Top clients (scoped to the period) ----
    client_count = {}
    for appointment in period_appointments:
        client_count[appointment.client_id] = (
            client_count.get(appointment.client_id, 0) + 1
        )

    top_clients = sorted(
        (
            {
                "id": cid,
                "name": clients_by_id[cid].full_name if cid in clients_by_id else "Cliente",
                "total": total,
            }
            for cid, total in client_count.items()
        ),
        key=lambda item: item["total"],
        reverse=True,
    )[:5]

    # ---- Inactive clients (last visit > INACTIVE_DAYS ago) ----
    last_visit = {}
    for appointment in appointments:
        if appointment.status == "cancelled":
            continue
        if appointment.scheduled_at > now:
            continue
        previous = last_visit.get(appointment.client_id)
        if previous is None or appointment.scheduled_at > previous:
            last_visit[appointment.client_id] = appointment.scheduled_at

    inactive_clients = []
    for cid, last_date in last_visit.items():
        days = (now - last_date).days
        if days > INACTIVE_DAYS:
            inactive_clients.append({
                "id": cid,
                "name": clients_by_id[cid].full_name if cid in clients_by_id else "Cliente",
                "days": days,
            })
    inactive_clients.sort(key=lambda item: item["days"], reverse=True)
    inactive_clients = inactive_clients[:5]

    # ---- Birthdays this month ----
    birthday_clients = [
        {
            "id": c.id,
            "name": c.full_name,
            "birth_date": c.birth_date,
        }
        for c in clients
        if c.birth_date and c.birth_date.month == current_month
    ][:5]

    # ---- Weekly distribution (scoped to the period) ----
    week_map = {day: 0 for day in WEEKDAYS}
    for appointment in period_appointments:
        # Python weekday(): Mon=0..Sun=6 ; map to WEEKDAYS (Sun=0..Sat=6)
        index = (appointment.scheduled_at.weekday() + 1) % 7
        week_map[WEEKDAYS[index]] += 1

    weekly_appointments = [
        {"day": day, "agendamentos": week_map[day]}
        for day in WEEKDAYS
    ]

    # ---- Revenue over the last 6 months ----
    monthly_revenue_chart = []
    for offset in range(5, -1, -1):
        month_index = current_month - 1 - offset
        year = current_year
        while month_index < 0:
            month_index += 12
            year -= 1

        target_month = month_index + 1

        revenue = sum(
            price_of(a)
            for a in appointments
            if _is_billable(a)
            and a.scheduled_at.month == target_month
            and a.scheduled_at.year == year
        )

        monthly_revenue_chart.append({
            "month": MONTHS[month_index],
            "revenue": revenue,
        })

    # ---- Alerts ----
    alerts = []

    goal_percent = (month_revenue / monthly_goal) * 100 if monthly_goal else 0
    alerts.append({
        "type": "success" if goal_percent >= 100 else "warning",
        "text": f"Meta atingida em {goal_percent:.0f}%",
    })

    if monthly_growth >= 0:
        alerts.append({
            "type": "success",
            "text": f"Crescimento de {monthly_growth:.1f}%",
        })
    else:
        alerts.append({
            "type": "danger",
            "text": f"Queda de {abs(monthly_growth):.1f}%",
        })

    if top_services:
        alerts.append({
            "type": "info",
            "text": f"Serviço líder: {top_services[0]['name']}",
        })

    if birthday_clients:
        alerts.append({
            "type": "info",
            "text": f"{len(birthday_clients)} aniversariantes este mês",
        })

    if len(tomorrow_list) < 3:
        alerts.append({
            "type": "warning",
            "text": "Poucos agendamentos amanhã",
        })

    return {
        "kpis": {
            "today_revenue": today_revenue,
            "today_appointments": today_appointments,
            "month_revenue": month_revenue,
            "previous_month_revenue": previous_month_revenue,
            "monthly_growth": monthly_growth,
            "forecast_revenue": forecast_revenue,
            "average_ticket": average_ticket,
            "occupancy_rate": occupancy_rate,
            "total_clients": len(clients),
            "new_clients_month": new_clients_month,
            "total_services": len(services),
            "average_rating": average_rating,
            "total_reviews": total_reviews,
            "monthly_goal": monthly_goal,
            "goal_progress": goal_progress,
        },
        "period": {
            "start": period_start,
            "end": period_end,
            "revenue": period_revenue,
            "appointments": period_count,
            "ticket": period_ticket,
        },
        "today_appointments_list": [
            _brief(a, clients_by_id, services_by_id, professionals_by_id)
            for a in today_list
        ],
        "tomorrow_appointments": [
            _brief(a, clients_by_id, services_by_id, professionals_by_id)
            for a in tomorrow_list
        ],
        "next_appointments": [
            _brief(a, clients_by_id, services_by_id, professionals_by_id)
            for a in upcoming
        ],
        "top_services": top_services,
        "top_clients": top_clients,
        "inactive_clients": inactive_clients,
        "birthday_clients": birthday_clients,
        "weekly_appointments": weekly_appointments,
        "monthly_revenue_chart": monthly_revenue_chart,
        "alerts": alerts,
    }
