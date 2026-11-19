# AGENTS.md

FastAPI + SQLAlchemy 2 REST API (JWT auth) backed by MySQL; the pytest suite
runs on in-memory SQLite. **Use Python 3.12 only** — the default `python3` is
3.14 and has none of the dependencies installed.

## Commands

```bash
python3.12 -m pytest                                 # all tests (no MySQL needed)
python3.12 -m pytest tests/test_users.py -k <name>   # single test
python3.12 -m uvicorn main:app --reload              # dev server (docs at /docs)
python3.12 create_admin.py                           # idempotent admin bootstrap
```

Do NOT use bare `pytest` or `uvicorn`: those binaries' shebangs point at Python
3.14 and fail. Ignore `venv/` — it is an empty 3.14 venv; dependencies live in
the 3.12 user site (`~/.local/lib/python3.12/site-packages`).

## Environment

- `.env` at repo root is required for everything, including tests
  (`core.config` instantiates `Settings()` at import; `DATABASE_URL` and
  `SECRET_KEY` have no defaults). Copy from `.env.example`.
- App startup needs a reachable MySQL at `DATABASE_URL`: `main.py` runs
  `Base.metadata.create_all()` at import time. There is no migration tool
  (no Alembic); schema comes from the models on startup. Tests don't need MySQL.
- `bcrypt` is pinned `<4.1.0` deliberately: passlib 1.7.4 breaks with newer
  bcrypt. Don't upgrade it in isolation.
- Test deps (`pytest`, `httpx`) are not listed in `requirements.txt`.

## Tests

- The suite runs on in-memory SQLite: `tests/conftest.py` reassigns
  `database.engine`/`SessionLocal` and compiles `PointColumn` (MySQL POINT) to
  BLOB **before** importing `main`. That import order is load-bearing — do not
  reorder conftest imports.
- Use fixtures `client`, `admin_headers`, `user_headers`; each test's DB changes
  roll back via the `db_session` transaction.

## Layout

- `api/v1/endpoints/` — route handlers, wired in `api/v1/router.py`, mounted at
  `/api/v1`.
- `core/` — config (pydantic-settings), models, schemas, auth (JWT + passlib),
  and the DB session.
- `core.models.PointColumn` — custom type storing coordinates as MySQL POINT
  (WKB via shapely); incidence endpoints accept `latitude`/`longitude`. Shapely
  is a required runtime dependency.

## Known environment issue

As of Nov 2026 the apt-managed `cryptography` in `/usr/lib/python3/dist-packages`
(46.0.5) has a mismatched `_rust` binding, so importing `pymysql`/`cryptography`
fails with `AttributeError: module ... has no attribute 'hashes'`. This is
machine state, not repo code. Fix with a clean user-site copy:

```bash
python3.12 -m pip install --user --force-reinstall cryptography
```
