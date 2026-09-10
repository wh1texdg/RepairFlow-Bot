# RepairFlow Roadmap

## Implemented

1. Architecture and modular project structure.
2. PostgreSQL data model with SQLAlchemy 2.x.
3. Async SQLAlchemy session.
4. Alembic initial migration.
5. Pydantic request validation.
6. aiogram 3 FSM request collection.
7. Request creation and client request list.
8. Repository and service layers.
9. Status workflow and audit history.
10. FastAPI REST endpoints.
11. JWT decoding and manager/admin authorization.
12. Manager seed command.
13. Google Sheets adapter with blocking SDK isolated from async event loop.
14. Telegram notification service.
15. APScheduler stale-request reminder.
16. Docker Compose with PostgreSQL, API, bot and scheduler.
17. Basic pytest tests.

## Production hardening still recommended

- Replace development token endpoint with a real authentication flow.
- Store Google credentials in a proper secret manager in production.
- Add retry/backoff and a persistent sync-outbox for guaranteed Sheets resync.
- Add API pagination metadata and filtering.
- Add request IDs/structured JSON logs.
- Add integration tests against PostgreSQL.
- Add rate limiting.
- Add webhook mode for Telegram.
- Add real admin dashboard if desired.
