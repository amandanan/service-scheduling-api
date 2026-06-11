# 🚀 Service Scheduling App

Full stack application built with **React + Vite** and **FastAPI**, featuring JWT authentication, appointment scheduling, client/service management, and an interactive calendar interface.

---

# 🧠 About the Project

This project is a complete **service scheduling system** designed to manage appointments in a practical and intuitive way.

The application allows users to:

* Register and authenticate securely
* Manage clients and services
* Configure weekly working hours
* Schedule appointments through an interactive calendar
* Share a public booking page with their own clients
* Search clients by name or CPF
* Search services by code or name
* Prevent schedule conflicts automatically
* View appointment durations dynamically
* Delete appointments directly from the calendar

The goal of this project was to practice modern **full stack development**, integrating a responsive frontend with a robust API backend.

---

# 🛠️ Tech Stack

## 💻 Frontend

* React
* Vite
* FullCalendar
* React Select
* Axios
* React Toastify
* React Icons
* Custom CSS

---

## ⚙️ Backend

* FastAPI
* SQLAlchemy
* SQLite
* JWT Authentication
* Passlib (password hashing)
* Pydantic

---

# 🔐 Features

## ✅ Authentication

* JWT login system
* Protected routes
* Secure password hashing

---

## 👥 Client Management

* Create clients
* Edit clients
* Delete clients
* Search patients by:

  * Name
  * CPF

---

## 🛠️ Service Management

* Create services
* Edit services
* Delete services
* Custom duration per service
* Supports appointments shorter than 60 minutes

Examples:

* 30 min
* 45 min
* 90 min
* 120 min

---

## 📅 Appointment System

* Interactive weekly calendar
* Monthly / weekly / daily view
* Click calendar to select time
* Dynamic appointment duration
* Visual schedule organization
* Delete appointments directly from calendar

---

## 🌐 Public Booking Page

Each user gets a unique, shareable booking link based on their business name (e.g. `/agendar/salao-da-amanda`).

On this page, clients can, without logging in:

* See the business name
* Choose a service
* Pick a date and an available time slot
* Fill in their personal details
* Confirm the appointment

The link is available on the **Working Hours** page and can be copied or opened directly.

The public endpoints are rate limited per IP (via `slowapi`) to protect against spam and abuse, since they require no authentication.

---

## 🚫 Schedule Conflict Blocking

The system automatically prevents overlapping appointments.

Example:

* Existing appointment:

  * 09:00 → 10:00

Blocked examples:

* 09:30
* 09:45
* 09:50

Allowed example:

* 10:00

---

## 🔎 Smart Search

### Patients

Search using:

* Patient name
* CPF

Example:

* Maria
* 12345678900

---

### Services

Search using:

* Service ID
* Service name

Example:

* 1
* Consultation

---

## 🎨 UI Features

* Modern interface
* Responsive layout
* Interactive calendar
* Visual confirmation cards
* Toast notifications
* Dark theme

---

# 📸 Screenshots

> Add screenshots here later

Examples:

* Login screen
* Dashboard
* Services page
* Appointments calendar
* Patient/service selection cards

---

# 🚀 Getting Started

## 🔧 Backend Setup

```bash
cd backend

python3 -m venv .venv

source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Configure environment variables:

```bash
cp .env.example .env
```

Edit `.env` and set a `SECRET_KEY` (generate one with `python -c "import secrets; print(secrets.token_hex(32))"`).

Apply database migrations:

```bash
alembic upgrade head
```

Run backend:

```bash
uvicorn app.main:app --reload
```

Backend runs at:

```bash
http://127.0.0.1:8000
```

### Running tests

```bash
pytest
```

### Creating a new migration

After changing a model, generate a migration and apply it:

```bash
alembic revision --autogenerate -m "describe your change"
alembic upgrade head
```

---

## 💻 Frontend Setup

```bash
cd frontend

npm install
```

Install additional libraries:

```bash
npm install axios react-router-dom react-toastify react-icons react-select
```

Install calendar dependencies:

```bash
npm install @fullcalendar/react
npm install @fullcalendar/daygrid
npm install @fullcalendar/timegrid
npm install @fullcalendar/interaction
```

Run frontend:

```bash
npm run dev
```

Frontend runs at:

```bash
http://localhost:5173
```

---

# 🔑 Authentication

The API uses JWT authentication.

After login:

* Token is generated
* Stored on frontend
* Automatically sent in protected requests

---

# 📂 Project Structure

```bash
service-scheduling-app/
│
├── backend/
│   ├── app/
│   │   ├── core/
│   │   ├── database/
│   │   ├── models/
│   │   ├── routes/
│   │   ├── schemas/
│   │   └── main.py
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── styles/
│   │   └── App.jsx
```

---

# 📌 Future Improvements

* Edit appointments
* Drag-and-drop scheduling
* Professional dashboard analytics
* Email reminders
* WhatsApp notifications
* User roles
* Holiday blocking
* Recurring appointments
* PostgreSQL support for production

---

# 👨‍💻 Author

Developed by Amanda Nanni as a full stack study project using React and FastAPI.


