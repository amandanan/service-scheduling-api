FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# WeasyPrint native dependencies (pango, cairo, gobject)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libpangoft2-1.0-0 \
    libcairo2 \
    libgdk-pixbuf2.0-0 \
    libfontconfig1 \
    fonts-liberation \
 && rm -rf /var/lib/apt/lists/*

# install dependencies first so they are cached across code changes
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# application code
COPY . .

EXPOSE 8000

# run database migrations, then start the API
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
