"""Interpreted-text insights for the PDF report.

Accepts pre-computed dicts (output of compute_stats, compute_metrics,
compute_hourly_distribution) — no database access, no duplicate calculation.
The caller is responsible for running the equivalent prior-period metrics
and passing them as prev_metrics for trend comparisons.
"""


def _money(value: float) -> str:
    return f"R$ {value:,.0f}".replace(",", ".")


def build_insights(
    stats: dict,
    metrics: dict,
    hourly: list[dict],
    prev_metrics: dict | None = None,
) -> list[dict]:
    """Return a list of {type, text} insight dicts for the PDF executive summary."""
    insights: list[dict] = []

    kpis = stats.get("kpis", {})
    monthly_goal = kpis.get("monthly_goal") or 0
    month_revenue = kpis.get("month_revenue", 0.0)
    goal_progress = kpis.get("goal_progress", 0.0)
    monthly_growth = kpis.get("monthly_growth", 0.0)

    # ── Goal progress ──────────────────────────────────────────────────────
    if monthly_goal:
        if goal_progress >= 100:
            insights.append({"type": "success", "text": "Meta mensal atingida."})
        else:
            remaining = monthly_goal - month_revenue
            severity = "warning" if goal_progress >= 60 else "danger"
            insights.append({
                "type": severity,
                "text": f"Meta mensal em {goal_progress:.0f}% — faltam {_money(remaining)}.",
            })

    # ── Month-over-month revenue trend (always calendar-month comparison) ──
    if monthly_growth >= 2:
        insights.append({
            "type": "success",
            "text": f"Faturamento cresceu {monthly_growth:.1f}% em relação ao mês anterior.",
        })
    elif monthly_growth <= -2:
        insights.append({
            "type": "danger",
            "text": f"Faturamento caiu {abs(monthly_growth):.1f}% em relação ao mês anterior.",
        })

    # ── No-show rate (current period) ─────────────────────────────────────
    no_show_rate = metrics.get("no_show_rate", 0.0)
    if no_show_rate > 15:
        insights.append({
            "type": "danger",
            "text": f"Taxa de no-show elevada: {no_show_rate:.1f}% dos atendimentos esperados.",
        })
    elif no_show_rate > 5:
        insights.append({
            "type": "warning",
            "text": f"Taxa de no-show em {no_show_rate:.1f}% no período.",
        })

    # ── Period-over-period comparisons ─────────────────────────────────────
    if prev_metrics:
        prev_no_show = prev_metrics.get("no_show_rate", 0.0)
        delta_ns = no_show_rate - prev_no_show
        if abs(delta_ns) >= 2:
            direction = "subiu" if delta_ns > 0 else "recuou"
            insights.append({
                "type": "danger" if delta_ns > 0 else "success",
                "text": (
                    f"No-show {direction} {abs(delta_ns):.1f} p.p."
                    f" em relação ao período anterior."
                ),
            })

        prev_cancel = prev_metrics.get("cancellation_rate", 0.0)
        curr_cancel = metrics.get("cancellation_rate", 0.0)
        delta_cancel = curr_cancel - prev_cancel
        if abs(delta_cancel) >= 3:
            direction = "subiu" if delta_cancel > 0 else "recuou"
            insights.append({
                "type": "warning" if delta_cancel > 0 else "success",
                "text": (
                    f"Taxa de cancelamento {direction} {abs(delta_cancel):.1f} p.p."
                    f" vs. período anterior."
                ),
            })

    # ── Cancellation attribution ───────────────────────────────────────────
    cb_client = metrics.get("cancelled_by_client", 0)
    cb_reception = metrics.get("cancelled_by_reception", 0)
    total_cancelled = cb_client + cb_reception
    if total_cancelled > 0:
        pct_client = round(cb_client / total_cancelled * 100)
        insights.append({
            "type": "info",
            "text": (
                f"Cancelamentos: {pct_client}% pelo cliente,"
                f" {100 - pct_client}% pela recepção."
            ),
        })

    # ── Revenue lost to no-shows (frozen price gap) ────────────────────────
    realized = metrics.get("realized_revenue", 0.0)
    expected = metrics.get("expected_revenue", 0.0)
    lost = expected - realized
    if expected > 0 and lost / expected > 0.10:
        insights.append({
            "type": "warning",
            "text": f"Receita não realizada por no-shows: {_money(lost)} no período.",
        })

    # ── Inactive clients (actionable) ─────────────────────────────────────
    inactive_total = stats.get("inactive_total", 0)
    if inactive_total > 0:
        plural = "clientes" if inactive_total > 1 else "cliente"
        insights.append({
            "type": "warning" if inactive_total < 10 else "danger",
            "text": (
                f"{inactive_total} {plural} sem retorno há mais de 90 dias."
                " Oportunidade de reativação."
            ),
        })

    # ── Top service ────────────────────────────────────────────────────────
    top_services = stats.get("top_services", [])
    if top_services:
        top = top_services[0]
        insights.append({
            "type": "info",
            "text": f"Serviço mais solicitado: {top['name']} ({top['total']} agendamentos).",
        })

    # ── Peak and quiet hours (decision 1b) ────────────────────────────────
    if hourly:
        peak = max(hourly, key=lambda h: h["agendamentos"])
        insights.append({
            "type": "info",
            "text": f"Horário de maior movimento: {peak['label']} ({peak['agendamentos']} agendamentos).",
        })
        if len(hourly) > 1:
            quiet = min(hourly, key=lambda h: h["agendamentos"])
            insights.append({
                "type": "info",
                "text": f"Horário de menor ocupação: {quiet['label']}.",
            })

    return insights
