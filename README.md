# Auth & Payment Links API 🚀

REST API with JWT authentication (access + refresh tokens), multi‑session support, and a headless payment link engine powered by Stripe. Fully containerized with Docker and PostgreSQL.

## Live Demo

- **Base URL**: [https://auth-paylink-engine-production.up.railway.app/](https://auth-paylink-engine-production.up.railway.app/)
- **Swagger UI**: [https://auth-paylink-engine-production.up.railway.app/docs](https://auth-paylink-engine-production.up.railway.app/docs)
- **ReDoc**: [https://auth-paylink-engine-production.up.railway.app/redoc](https://auth-paylink-engine-production.up.railway.app/redoc)

> This public deployment is intended for testing and portfolio purposes.  
> Feel free to register a temporary user and explore the API.

## Tech Stack

- Python 3.14 + FastAPI (async)
- SQLAlchemy 2.0 + asyncpg
- PostgreSQL + Redis + Celery
- JWT (python‑jose), bcrypt
- Stripe SDK
- Docker, Poetry, pytest

## API Endpoints (Summary)

| Method | Endpoint                     | Auth required | Description                                      |
| ------ | ---------------------------- | ------------- | ------------------------------------------------ |
| POST   | `/users/`                    | ❌             | Create a new user                                |
| POST   | `/users/login`               | ❌             | Authenticate, get access & refresh tokens        |
| POST   | `/users/refresh`             | ❌*            | Get new access token (requires refresh token)    |
| POST   | `/users/logout`              | ❌*            | Revoke the current refresh token                 |
| GET    | `/users/me`                  | ✅             | Get current user info                            |
| GET    | `/health`                    | ❌             | Health check (API + DB status)                   |

*These endpoints expect the token in the `Authorization: Bearer <token>` header.*

**Authentication security**: Refresh tokens are stored as SHA256 hashes, never in plain text. Each token contains a unique `jti` (UUID) to guarantee individuality and support fine‑grained revocation. Multi‑session is fully supported: every login creates a new refresh token without invalidating previous ones, allowing users to stay connected across multiple devices. Tokens can be revoked individually via the logout endpoint, and sessions can be listed and remotely revoked using dedicated endpoints.

## Payment Links (Headless Billing)

| Method | Endpoint                       | Auth required | Description                                      |
| ------ | ------------------------------ | ------------- | ------------------------------------------------ |
| POST   | `/payment-links/`              | ✅ (access)    | Create a new payment link                        |
| GET    | `/payment-links/`              | ✅ (access)    | List all payment links for the authenticated user |
| GET    | `/pay/{public_id}`             | ❌             | Public endpoint – returns Stripe Checkout URL    |
| POST   | `/webhooks/stripe`             | ❌ (webhook)   | Stripe webhook to update payment status          |

After creating a payment link, share the public URL (`/pay/{public_id}`) with your customer. They pay via Stripe Checkout (test cards: `4242 4242 4242 4242`). Your application receives a webhook and updates the payment status automatically.

## Author

Backend developer building secure, scalable APIs with Python.
