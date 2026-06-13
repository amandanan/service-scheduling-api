FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# install dependencies first so they are cached across code changes
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# application code
COPY . .

EXPOSE 8000

# run database migrations, then start the API
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
