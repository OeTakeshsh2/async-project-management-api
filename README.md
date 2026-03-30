# Project Management API 🚀

REST API designed with production practices, built with FastAPI, featuring JWT authentication, async database handling, and a scalable layered architecture.

---

## Tech Stack

* Python 3.14
* FastAPI
* SQLAlchemy (async)
* PostgreSQL
* Poetry / Docker
* JWT Authentication

---

## Project Structure

```
app/
│── core/        # Core logic (DB, security, auth)
│── models/      # SQLAlchemy models
│── schemas/     # Pydantic schemas (validation)
│── routes/      # API endpoints
│── main.py      # Application entry point
```

---

## Setup

### 0. Environment variables

Create a `.env` file with:

```env
DATABASE_URL=...
SECRET_KEY=...
```

### 1. Install dependencies

```bash
poetry install
```

### 2. Run the server

```bash
poetry run uvicorn app.main:app --reload
```

---

## Run with Docker

```bash
docker-compose up --build
```

---

## Authentication

This API uses **JWT (JSON Web Tokens)** for authentication.

Tokens are stateless and must be included in the `Authorization` header for protected endpoints.

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

## API Endpoints

### Users

* `POST /users/` → Create user
* `POST /users/login` → Authenticate user
* `GET /users/me` → Get current user (protected)

---

## Design Decisions

* **Async SQLAlchemy** → better performance & scalability
* **Layered architecture** → improves maintainability and testability
* **JWT auth** → stateless authentication
* **PostgreSQL** → production-ready database

---

## Database Design

### users

| Field    | Type   | Notes           |
| -------- | ------ | --------------- |
| id       | int    | Primary key     |
| email    | string | Unique          |
| password | string | Hashed (bcrypt) |

---

## Security & Implementation Notes

* Passwords are securely hashed using **bcrypt**
* Tokens include expiration (`exp`)
* Tables are auto-created on startup via SQLAlchemy metadata

---

## 🧑‍💻 Author

Backend developer focused on building secure and scalable APIs with Python.

