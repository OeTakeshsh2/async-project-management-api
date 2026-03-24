# Project Management API

Backend REST API built with FastAPI for managing users, projects, and tasks.

---

## 🚀 Tech Stack

* Python 3.14
* FastAPI
* SQLAlchemy (async)
* PostgreSQL
* Poetry
* JWT Authentication

---

## 📁 Project Structure

```
app/
│── core/        # Core logic (DB, security, auth)
│── models/      # SQLAlchemy models
│── schemas/     # Pydantic schemas (validation)
│── routes/      # API endpoints
│── main.py      # Application entry point
```

---

## ⚙️ Setup

### 1. Install dependencies

```bash
poetry install
```

### 2. Run the server

```bash
poetry run uvicorn app.main:app --reload
```

---

## 🔐 Authentication

This API uses **JWT (JSON Web Tokens)** for authentication.

### Flow

1. Register a user → `POST /users/`
2. Login → `POST /users/login`
3. Receive `access_token`
4. Use token in protected routes:

```bash
Authorization: Bearer <your_token>
```

### Example

```bash
curl -X GET "http://127.0.0.1:8000/users/me" \
-H "Authorization: Bearer <your_token>"
```

---

## 📌 Available Endpoints

### Users

* `POST /users/` → Create user
* `POST /users/login` → Authenticate user
* `GET /users/me` → Get current user (protected)

---

## 🧠 Design Decisions

* **Async SQLAlchemy** → better performance & scalability
* **Layered architecture** → separation of concerns
* **JWT auth** → stateless authentication
* **PostgreSQL** → production-ready database

---

## 🗄️ Database Design

### users

| Field    | Type   | Notes           |
| -------- | ------ | --------------- |
| id       | int    | Primary key     |
| email    | string | Unique          |
| password | string | Hashed (bcrypt) |

---

## ⚠️ Notes

* Passwords are securely hashed using **bcrypt**
* Tokens include expiration (`exp`)
* Tables are auto-created on startup via SQLAlchemy metadata

---

## 📌 TODO

* [ ] Projects & Tasks models
* [ ] Role-based authorization
* [ ] Refresh tokens
* [ ] Docker setup
* [ ] Automated tests

---

## 🧑‍💻 Author

Backend Developer focused on Python & scalable APIs.

