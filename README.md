# RepairFlow

**RepairFlow** is a portfolio backend project that turns a Telegram renovation questionnaire into a managed CRM workflow.

## Stack

- Python 3.12
- aiogram 3.x
- FastAPI
- PostgreSQL
- SQLAlchemy 2.x + asyncpg
- Alembic
- Pydantic v2
- JWT
- APScheduler
- Google Sheets API
- Docker Compose
- pytest

## Main scenario

```text
Client
  ↓
Telegram bot
  ↓
FSM questionnaire
  ↓
Confirmation
  ↓
RequestService
  ↓
PostgreSQL
  ├── status = NEW
  └── status history
  ↓
Manager notification
  ↓
Google Sheets projection
```

Google Sheets is not the source of truth.

## Run

```bash
cp .env.example .env
# fill BOT_TOKEN, MANAGER_IDS and JWT_SECRET

docker compose up --build
docker compose exec api alembic upgrade head
```

API docs:

```text
http://localhost:8000/docs
```

Health:

```text
http://localhost:8000/health
```

## Create first manager

After migration:

```bash
docker compose exec api python -m app.scripts.seed_manager 123456789 "Main Manager" ADMIN
```

Then, in development, obtain a JWT through:

```text
POST /api/v1/auth/dev-token?manager_id=<DB_ID>
```

Do not use that endpoint in production.

## Tests

```bash
pytest -q
```

## Environment

See `.env.example`.

Never commit `.env` or Google credentials.

## Project structure

```text
app/
├── api/             # FastAPI routes, schemas, auth dependencies
├── bot/             # Telegram handlers, FSM and keyboards
├── core/            # config, security, exceptions, logging
├── database/        # SQLAlchemy models/session
├── integrations/    # Telegram notifications + Google Sheets
├── repositories/    # DB queries
├── scheduler/       # APScheduler jobs
├── scripts/         # operational commands
└── services/        # business logic
```

See `docs/FINAL_ARCHITECTURE.md` for the architecture diagram.
