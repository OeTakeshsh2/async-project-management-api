# Project Management API 🚀

REST API with production-ready practices, built with FastAPI. Features JWT authentication (access + refresh tokens), refresh token hashing, revocation, single‑session policy, and async database handling. Fully containerized with Docker and PostgreSQL.

---

## Tech Stack

* **Python 3.14**
* **FastAPI** (async)
* **SQLAlchemy** (async + ORM)
* **PostgreSQL** (via asyncpg)
* **Alembic** (migrations)
* **JWT** (python-jose)
* **bcrypt** (passlib)
* **Docker** + docker-compose
* **Poetry** (inside container)

---

## Project Structure

```text
app/
├── core/      # Core logic: DB, security, auth, dependencies
├── models/    # SQLAlchemy ORM models
├── schemas/   # Pydantic schemas (validation)
├── routes/    # API endpoints
├── main.py    # Application entry point
migrations/    # Alembic migration scripts
alembic.ini
docker-compose.yml
Dockerfile
.env.example
```

---

## Run with Docker

1. **Clone the repository** and create a `.env` file from `.env.example`:

```bash
cp .env.example .env
edit .env with your own secrets
```

2. **Start the containers**:

```bash
docker-compose up --build
```

This will start both the FastAPI app (port 8000) and PostgreSQL.

3. **Apply database migrations** (automatically done on first run, but can be run manually):

```bash
docker exec -it p_api-api-l alembic upgrade head
```

4. **Access the interactive API docs**:

* Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
* ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## Authentication & Token Flow

The API uses JWT with **access** and **refresh tokens**:

| Token         | Lifetime | Purpose                              |
| ------------- | -------- | ------------------------------------ |
| Access token  | 15 min   | Authenticate protected endpoints     |
| Refresh token | 7 days   | Obtain new access token when expired |

### 🔐 Security Features

* Refresh tokens are hashed (SHA256) and never stored in plain text.
* Single session per user: each login invalidates previous refresh tokens.
* Token revocation is supported via logout.
* Token type validation ensures tokens are used only for intended endpoints.
* Expiration checks reject expired tokens.

### 🔁 Flow

1. Register a user → `POST /users/`
2. Login → `POST /users/login` → receive `access_token` and `refresh_token`
3. Use the `access_token` in the Authorization header for protected endpoints:

```bash
Authorization: Bearer <access_token>
```

4. When the access token expires, refresh it using:

```bash
POST /users/refresh
Authorization: Bearer <refresh_token>
```

5. Logout → `POST /users/logout` (requires refresh token) – revokes the token.

---

## API Endpoints

| Method | Endpoint       | Auth required | Description                             |
| ------ | -------------- | ------------- | --------------------------------------- |
| POST   | /users/        | ❌             | Create a new user                       |
| POST   | /users/login   | ❌             | Authenticate, get tokens                |
| POST   | /users/refresh | ❌*            | Get new access token (requires refresh) |
| POST   | /users/logout  | ❌*            | Revoke refresh token                    |
| GET    | /users/me      | ✅             | Get current user info (access token)    |

*These endpoints expect the token in the Authorization header.

### Example requests with curl

**Login**

```bash
curl -X POST http://localhost:8000/users/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=your@email.com&password=yourpassword"
```

**Get current user (protected)**

```bash
curl -X GET http://localhost:8000/users/me \
  -H "Authorization: Bearer <access_token>"
```

**Refresh access token**

```bash
curl -X POST http://localhost:8000/users/refresh \
  -H "Authorization: Bearer <refresh_token>"
```

**Logout (revoke refresh token)**

```bash
curl -X POST http://localhost:8000/users/logout \
  -H "Authorization: Bearer <refresh_token>"
```

---

## Database Design

### Users Table

| Column   | Type    | Description        |
| -------- | ------- | ------------------ |
| id       | integer | Primary key        |
| email    | string  | Unique, indexed    |
| password | string  | Hashed with bcrypt |

### User Tokens Table

| Column     | Type         | Description                   |
| ---------- | ------------ | ----------------------------- |
| id         | integer      | Primary key                   |
| user_id    | integer (FK) | References users.id           |
| token_hash | string(64)   | SHA256 of refresh token       |
| created_at | timestamptz  | Default now()                 |
| revoked    | boolean      | False by default              |
| expires_at | timestamptz  | Nullable, expiration of token |

---

## Development Notes

* Docker is the recommended way to run the project; Poetry is used inside the container.
* Migrations are managed with Alembic:

```bash
docker exec -it p_api-api-1 alembic revision --autogenerate -m "description"
docker exec -it p_api-api-1 alembic upgrade head
```

* Async database operations are handled with `asyncpg`.
* Environment variables are loaded from `.env` via Pydantic's `BaseSettings`.

---

## Security & Implementation Notes

* Passwords are hashed with bcrypt.
* Access tokens contain `user_id` and `sub` (email) for quick identification.
* Refresh token hashing prevents token theft if the database is compromised.
* Single session enforced by deleting previous refresh tokens on login.
* Revoked tokens are checked in `/refresh` endpoint.
* Token types are validated in every operation.

---

## Future Improvements (Roadmap)

* Rotación de refresh tokens (invalidar y emitir uno nuevo en cada refresh)
* Logging estructurado con structlog
* Rate limiting en login/refresh
* Registro de user_agent / device_info en tokens
* Endpoints para listar y revocar sesiones activas
* Testing unitario y de integración

---

## 🧑‍💻 Author

Backend developer building secure, scalable APIs with Python.

