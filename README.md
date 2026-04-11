# Project Management API 🚀

REST API with production-ready practices, built with FastAPI. Features JWT authentication (access + refresh tokens), refresh token hashing, revocation, multi-session support, structured logging with correlation ID, and async database handling. Fully containerized with Docker and PostgreSQL.

## Live Demo

- API Base URL:https://auth-paylink-engine-production.up.railway.app/ 
- Swagger UI:https://auth-paylink-engine-production.up.railway.app/docs
- ReDoc:https://auth-paylink-engine-production.up.railway.app/redoc
> Note: This public deployment is intended for testing and portfolio purposes.
> Feel free to register a temporary user and explore the API.

## Tech Stack

- Python 3.14
- FastAPI (async)
- SQLAlchemy (async + ORM)
- PostgreSQL (via asyncpg)
- Alembic (migrations)
- JWT (python-jose)
- bcrypt (passlib)
- Docker + docker-compose
- Poetry (inside container)
- pytest + pytest-asyncio (testing)
- aiosqlite (in-memory DB for tests)

## Project Structure
```text
app/
├── core/
│   ├── config.py          # Settings (Pydantic)
│   ├── database.py        # Async DB engine, session
│   ├── security.py        # Password hashing
│   ├── auth.py            # JWT creation, validation, token storage
│   ├── dependencies.py    # get_current_user, etc.
│   ├── logging.py         # Logging setup with correlation ID
│   └── context.py         # ContextVar for correlation ID
├── middleware/
│   └── correlation.py     # Correlation ID middleware
├── models/                # SQLAlchemy ORM models (User, UserToken)
├── schemas/               # Pydantic schemas
├── routes/
│   ├── user.py            # Authentication endpoints
│   └── health.py          # Health check endpoint
├── main.py                # Application entry point
migrations/                # Alembic migration scripts
tests/                     # pytest suite (unit + integration)
├── conftest.py            # Fixtures (SQLite in-memory, client)
├── unit/
└── integration/
    └── test_users.py      # 10 integration tests
alembic.ini
docker-compose.yml
Dockerfile
.env.example
pyproject.toml
```

## Run with Docker

1. Clone the repository and create a `.env` file from `.env.example`:

cp .env.example .env
edit .env with your own secrets

2. Start the containers:

docker-compose up --build

This will start both the FastAPI app (port 8000) and PostgreSQL.

3. Apply database migrations (automatically done on first run, but can be run manually):

docker exec -it p_api-api-1 alembic upgrade head

4. Access the interactive API docs:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Authentication & Token Flow

The API uses JWT with access and refresh tokens:

| Token | Lifetime | Purpose |
|--------|----------|---------|
| Access token | 15 min | Authenticate protected endpoints |
| Refresh token | 7 days | Obtain new access token when expired |

## Security Features

- Refresh tokens are hashed (SHA256) and never stored in plain text.
- Multi-session support: each login creates a new refresh token without invalidating previous ones. Users can be logged in from multiple devices simultaneously.
- Token revocation is supported via logout (revokes only the token used) and via remote session revocation.
- Each token contains a unique jti (UUID) to guarantee uniqueness and enable individual revocation.
- Token type validation ensures tokens are used only for intended endpoints.
- Expiration checks reject expired tokens.

## Session Management

The API provides endpoints to list and revoke active sessions (refresh tokens):

| Method | Endpoint | Auth required | Description |
|--------|----------|---------------|-------------|
| GET | /users/sessions | ✅ (access) | List all active sessions for the user |
| DELETE | /users/sessions/{id} | ✅ (access) | Revoke a specific session (logout remote) |

Each session stores device name (User-Agent), IP address, creation time and last used time.

## Authentication Flow

1. Register a user → POST /users/

2. Login → POST /users/login → receive access_token and refresh_token

3. Use the access_token in the Authorization header for protected endpoints:

Authorization: Bearer <access_token>

4. When the access token expires, refresh it using:

POST /users/refresh
Authorization: Bearer <refresh_token>

5. Logout (revoke current refresh token) → POST /users/logout with the same header.

## API Endpoints

| Method | Endpoint | Auth required | Description |
|--------|----------|---------------|-------------|
| POST | /users/ | ❌ | Create a new user |
| POST | /users/login | ❌ | Authenticate, get tokens |
| POST | /users/refresh | ❌* | Get new access token (requires refresh token) |
| POST | /users/logout | ❌* | Revoke the current refresh token |
| GET | /users/me | ✅ | Get current user info (access token) |
| GET | /users/sessions | ✅ | List all active sessions for the authenticated user |
| DELETE | /users/sessions/{id} | ✅ | Revoke a specific session (logout remote) |
| GET | /health | ❌ | Health check (API + DB status) |

*These endpoints expect the token in the Authorization header.*

## Database Design

### Users Table

| Column | Type | Description |
|--------|------|-------------|
| id | integer | Primary key |
| email | string | Unique, indexed |
| password | string | Hashed with bcrypt |

### User Tokens Table

| Column | Type | Description |
|--------|------|-------------|
| id | integer | Primary key |
| user_id | integer (FK) | References users.id |
| token_hash | string(64) | SHA256 of refresh token |
| created_at | timestamptz | Default now() |
| revoked | boolean | False by default |
| expires_at | timestamptz | Nullable, expiration of token |
| device_name | string(100) | User-Agent (first 100 chars) |
| ip_address | string(45) | Client IP address (IPv4/IPv6) |
| last_used_at | timestamptz | Timestamp of last refresh using this token |

## Testing

The project includes a complete test suite using pytest and pytest-asyncio.

- Unit tests: pure functions in auth.py (hashing, token creation, decoding).
- Integration tests: 10 tests covering the full authentication flow (register, login, refresh, logout, get me, sessions, health check).
- Test database: SQLite in-memory, created and destroyed per test session. Fixtures ensure isolation.
- Mocked environment variables: tests do not depend on a .env file; all required settings are set programmatically.

Run tests locally:

poetry run pytest tests/ -v

All tests pass (10/10) and execute in under 3 seconds.

## Logging

Structured logging is implemented using Python's standard logging module with a custom correlation ID middleware.

- Every request receives a X-Correlation-ID header (generated if not provided).
- Log entries include the correlation ID, timestamp, logger name, level, and message.
- Logs are written to stdout (suitable for Docker and cloud platforms like Railway).
- Authentication events (login success/failure, token refresh, logout) are logged at INFO/WARNING level.
- Health check and database errors are logged as ERROR.

Example log line:

2025-04-09 10:00:00 - app - INFO - [abc123] → POST /users/login

## Health Check

The endpoint GET /health verifies the API and database connectivity:

- Performs a simple SELECT 1 on the database.
- Returns 200 OK with {"status":"ok","database":"connected"} if healthy.
- Returns 503 Service Unavailable with {"status":"degraded","database":"disconnected"} on database error.
- Used for container orchestration (Docker health checks, Kubernetes liveness probes).

## Development Notes

- Docker is the recommended way to run the project; Poetry is used inside the container.
- Migrations are managed with Alembic:

docker exec -it p_api-api-1 alembic revision --autogenerate -m "description"
docker exec -it p_api-api-1 alembic upgrade head

- Async database operations are handled with asyncpg.
- Environment variables are loaded from .env via Pydantic's BaseSettings.
- For testing, SQLite in-memory is used to avoid PostgreSQL dependency.

## Security & Implementation Notes

- Passwords are hashed with bcrypt.
- Access tokens contain user_id, sub (email), exp, iat, and a unique jti.
- Refresh token hashing prevents token theft if the database is compromised.
- Multi-session: store_refresh_token inserts a new token without deleting previous ones.
- Revoked tokens are filtered in verify_refresh_token by revoked=False.
- Sessions can be listed and remotely revoked via /users/sessions endpoints.
- Correlation ID middleware helps trace requests across logs.
- Health check endpoint provides monitoring capability.

## Future Improvements (Roadmap)

- ~~Multi-session support~~ (completed)
- ~~Structured logging with correlation ID~~ (completed)
- ~~Full integration test suite~~ (completed)
- ~~Health check endpoint~~ (completed)
- ~~Deployment on Railway~~ (completed)
- Refresh token rotation (invalidate old refresh token and issue a new one on each refresh)
- Rate limiting on login/refresh endpoints
- Email verification for new users
- Two-factor authentication (TOTP)

## Author

Backend developer building secure, scalable APIs with Python.
