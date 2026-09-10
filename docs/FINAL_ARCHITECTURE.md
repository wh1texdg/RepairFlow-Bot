# RepairFlow — Final Architecture

```text
                         ┌─────────────────┐
                         │ Telegram Client │
                         └────────┬────────┘
                                  │
                         aiogram 3 / FSM
                                  │
                         ┌────────▼────────┐
                         │ Bot Handlers    │
                         └────────┬────────┘
                                  │
                    ┌─────────────▼─────────────┐
                    │      Service Layer        │
                    │ RequestService/UserService│
                    └───────┬─────────┬──────────┘
                            │         │
                    ┌───────▼───┐ ┌──▼────────────────┐
                    │Repositories│ │ Integrations      │
                    │ SQLAlchemy  │ │ Telegram/Sheets   │
                    └───────┬────┘ └───────────────────┘
                            │
                     ┌──────▼──────┐
                     │ PostgreSQL  │
                     │ source truth│
                     └─────────────┘

                         ┌───────────┐
                         │ FastAPI   │
                         │ REST/JWT  │
                         └─────┬─────┘
                               │
                         Service Layer

                         ┌───────────┐
                         │Scheduler  │
                         │APScheduler│
                         └─────┬─────┘
                               │
                         Repository +
                         Notifications
```

## Why this architecture

- Telegram and HTTP are only entry points.
- Business rules live in services.
- Database queries live in repositories.
- PostgreSQL is the source of truth.
- Google Sheets is an external projection and can fail independently.
- Status history provides an audit trail.
- Async is used for database and Telegram I/O.
- Blocking Google client work is moved to an executor.
- Docker Compose keeps local deployment reproducible.
