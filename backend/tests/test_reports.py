"""Tests for PDF and CSV report endpoints."""
from tests.test_dashboard import _setup_business, _book, _set_scheduled_at
from tests._dates import at
from datetime import datetime


def test_pdf_requires_auth(client):
    response = client.get("/dashboard/report.pdf")
    assert response.status_code == 401


def test_csv_requires_auth(client):
    response = client.get("/dashboard/export.csv")
    assert response.status_code == 401


def test_pdf_empty_business(client):
    """PDF endpoint returns valid PDF bytes even with no appointments."""
    headers, *_ = _setup_business(client)

    response = client.get("/dashboard/report.pdf", headers=headers)

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    # A minimal WeasyPrint PDF is several kilobytes; ensure we got real content
    assert len(response.content) > 2_000
    assert response.content[:4] == b"%PDF"


def test_pdf_with_period_filter(client):
    """Period query params are accepted and reflected in the generated PDF."""
    headers, slug, service_id, professional_id = _setup_business(client)

    _set_scheduled_at(
        _book(client, slug, service_id, professional_id, "16899555468", at(10))[
            "public_token"
        ],
        datetime.now().replace(hour=10, minute=0, second=0, microsecond=0),
    )

    today = datetime.now().date().isoformat()
    response = client.get(
        f"/dashboard/report.pdf?start_date={today}&end_date={today}",
        headers=headers,
    )

    assert response.status_code == 200
    assert response.content[:4] == b"%PDF"
    assert len(response.content) > 2_000


def test_csv_empty_business(client):
    """CSV export returns valid CSV with section headers even with no data."""
    headers, *_ = _setup_business(client)

    response = client.get("/dashboard/export.csv", headers=headers)

    assert response.status_code == 200
    assert "text/csv" in response.headers["content-type"]
    body = response.text
    assert "Receita por Serviço" in body
    assert "Serviços Mais Solicitados" in body
    assert "Top Clientes" in body
    assert "Clientes Sem Retorno" in body


def test_csv_with_data(client):
    """CSV contains service revenue rows when completed appointments exist."""
    headers, slug, service_id, professional_id = _setup_business(client)

    booking = _book(
        client, slug, service_id, professional_id, "16899555468", at(11)
    )
    _set_scheduled_at(
        booking["public_token"],
        datetime.now().replace(hour=11, minute=0, second=0, microsecond=0),
    )
    # mark as completed so it shows up in realized revenue
    client.patch(
        f"/appointments/{booking['id']}/complete",
        headers=headers,
    )

    response = client.get("/dashboard/export.csv", headers=headers)
    assert response.status_code == 200
    assert "Corte" in response.text
