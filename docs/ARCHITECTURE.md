# RepairFlow Architecture

## Layers

### Presentation
- `app/bot/` — Telegram and FSM.
- `app/api/` — HTTP REST API.
- `app/scheduler/` — scheduled jobs.

### Business logic
- `app/services/` — application use cases and status rules.

### Persistence
- `app/repositories/` — database access.
- `app/database/` — SQLAlchemy models/session.

### Integrations
- `app/integrations/notifications.py`
- `app/integrations/google_sheets.py`

### Core
- configuration
- logging
- exceptions
- security
- dependency providers

## Principles

1. Handlers/routes do not contain business rules.
2. Services coordinate use cases.
3. Repositories contain persistence queries.
4. PostgreSQL is authoritative.
5. External integrations fail independently.
6. Status history is append-only audit data.
7. Async I/O is used for Telegram, HTTP and PostgreSQL paths.
8. Migrations are managed by Alembic.
