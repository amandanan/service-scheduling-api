from datetime import datetime, date

from pydantic import BaseModel


class DashboardKPIs(BaseModel):

    today_revenue: float
    today_appointments: int

    month_revenue: float
    previous_month_revenue: float
    monthly_growth: float

    forecast_revenue: float
    average_ticket: float
    occupancy_rate: int

    total_clients: int
    new_clients_month: int
    total_services: int

    average_rating: float | None
    total_reviews: int

    monthly_goal: float
    goal_progress: float


class AppointmentBrief(BaseModel):

    id: int
    client: str
    service: str
    professional: str
    scheduled_at: datetime
    time: str


class RankItem(BaseModel):

    name: str
    total: int


class ClientRankItem(BaseModel):

    id: int
    name: str
    total: int


class InactiveClientItem(BaseModel):

    id: int
    name: str
    days: int


class BirthdayItem(BaseModel):

    id: int
    name: str
    birth_date: date


class WeekdayPoint(BaseModel):

    day: str
    agendamentos: int


class RevenuePoint(BaseModel):

    month: str
    revenue: float


class DashboardAlert(BaseModel):

    type: str
    text: str


class PeriodSummary(BaseModel):

    start: date
    end: date
    revenue: float
    appointments: int
    ticket: float


class DashboardStats(BaseModel):

    kpis: DashboardKPIs

    period: PeriodSummary

    today_appointments_list: list[AppointmentBrief]
    tomorrow_appointments: list[AppointmentBrief]
    next_appointments: list[AppointmentBrief]

    top_services: list[RankItem]
    top_clients: list[ClientRankItem]
    inactive_clients: list[InactiveClientItem]
    birthday_clients: list[BirthdayItem]

    weekly_appointments: list[WeekdayPoint]
    monthly_revenue_chart: list[RevenuePoint]

    alerts: list[DashboardAlert]
