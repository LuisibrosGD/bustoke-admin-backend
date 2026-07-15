# Bustoke Admin Backend — Agent Guide

## Dev Commands

```bash
uvicorn app.main:app --host 0.0.0.0 --port 5000 --reload   # dev server
alembic upgrade head                                         # apply migrations
alembic revision --autogenerate -m "msg"                     # create migration
pip install -r requirements.txt                              # install deps
```

No tests, linter, formatter, or typechecker configured. Do not attempt to run them.

## Architecture

**FastAPI + async SQLAlchemy 2.x + Pydantic v2 + PostgreSQL 15.** All DB operations are async using the `select()` style (never legacy `Query` API).

Every module under `app/modules/<name>/` follows a 4-file pattern:
`__init__.py`, `models.py`, `schemas.py`, `service.py`, `router.py`

Modules without models (`dashboard/`, `reportes/`, `public/`) skip `models.py`.

## Schema Convention (critical)

All Pydantic schemas use **snake_case field names** but expose **camelCase via `Field(alias=...)`**:

```python
class ViajeOut(BaseModel):
    id_ruta: int = Field(alias="idRuta")
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
```

Every `Out` schema must follow this pattern.

## Auth Dependencies

From `app/dependencies.py`:
- `DbDep` — async SQLAlchemy session
- `CurrentUser` — any valid JWT
- `AdminOrSuper` — `admin_agencia` or `superadmin` role
- `SuperAdmin` — `superadmin` role only
- `ApiKeyAuth` — validates `x-api-key` header

List endpoints must filter by `id_agencia` from JWT when user role is `admin_agencia`.

## Error Handling

Raise custom exceptions from `app.core.exceptions`:
`NotFoundException` (404), `UnauthorizedException` (401), `ForbiddenException` (403), `BadRequestException` (400), `ConflictException` (409).

## Alembic

- Initial migration (001) is an **empty baseline** — DB is created externally via SQL script (not in repo).
- Import **all models** in `alembic/env.py` for `--autogenerate` to detect new tables.

## Lifespan Quirk

`app/main.py` lifespan manually creates the `Pago` table (dynamic ENUM workaround) via `metadata.create_all`. The `Pago` model import at the top of `main.py` exists solely for this.

## Routes

| Prefix | Purpose |
|--------|---------|
| `/admin/<module>` | Admin CRUD (JWT auth) |
| `/api/v1/` | Public endpoints (API Key auth) |
| `/reports` | Excel report downloads |
