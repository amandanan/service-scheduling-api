# 🚀 Service Scheduling App

Full stack application built with **React** and **FastAPI**, featuring authentication with JWT and appointment management.

---

## 🧠 About the Project

This project is a **service scheduling system**, where users can:

- Register and log in securely
- Manage clients and services
- Schedule appointments
- Access protected routes using JWT authentication

It was developed to practice **full stack development**, integrating a modern frontend with a robust backend API.

---

## 🛠️ Tech Stack

### 💻 Frontend
- React (Vite)
- CSS (custom modern UI)
- Responsive design

### ⚙️ Backend
- FastAPI
- SQLAlchemy
- JWT Authentication
- Passlib (password hashing)

---

## 🔐 Features

- ✅ User authentication (JWT)
- ✅ Secure password hashing
- ✅ Protected routes
- ✅ Appointment scheduling
- ✅ Responsive UI
- ✅ Modern design (dark theme)

---

## 📸 Screenshots

> (adicione prints aqui depois)

---

## 🚀 Getting Started

### 🔧 Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate

pip install fastapi uvicorn sqlalchemy python-jose[cryptography] passlib[bcrypt] pydantic[email]

uvicorn app.main:app --reload

