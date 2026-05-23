# FastAPI Store

A minimal **FastAPI** learning project that exposes a versioned REST API for **users**. Data is stored in an in-memory list (no database yet), which keeps the codebase small while demonstrating common patterns:

- Pydantic models for request/response validation (`User`, `CreateUser`, `UpdateUser`, `UserReplace`)
- REST conventions: `POST` (create), `GET` (list & detail), `PATCH` (partial update), `PUT` (full replace), `DELETE`
- UUIDs in URL paths (not list indices)
- OpenAPI documentation with grouped routes (`tags`) and documented `404` responses

The app entry point is `main.py` at the repository root. Static files and Jinja2 templates are wired for future UI work.

## Requirements

- **Python 3.12+** (see `.python-version`)
- **[uv](https://docs.astral.sh/uv/)** - package and environment manager used by this project (if `uv` is needed : `curl -LsSf https://astral.sh/uv/install.sh | sh`)

## Installation

```bash
git clone git@github.com:GeraldB69/fastapi_store.git
cd fastapi_store
uv sync
```

Creates `.venv` and installs dependencies from `pyproject.toml` / `uv.lock`.

Include dev dependencies (pytest) with:

```bash
uv sync --dev
```

## Run it


| Action             | With venv                   | Without venv         |
| ------------------ | --------------------------- | -------------------- |
| Enter (activate)   | `source .venv/bin/activate` |                      |
| Add a package      | `uv add <package-name>`*    |                      |
| Run the applicaton | `fastapi dev`               | `uv run fastapi dev` |
| Run tests          | `pytest`                    | `uv run pytest`      |
| Exit (deactivate)  | `deactivate`                |                      |


`*` `uv add` updates `pyproject.toml` and `uv.lock`; run it from the project root (venv activated or not).

### Links


| Resource                   | URL                                                                      |
| -------------------------- | ------------------------------------------------------------------------ |
| API root                   | [http://127.0.0.1:8000/](http://127.0.0.1:8000/)                         |
| Interactive docs (Swagger) | [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)                 |
| Alternative docs (ReDoc)   | [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)               |
| OpenAPI schema             | [http://127.0.0.1:8000/openapi.json](http://127.0.0.1:8000/openapi.json) |


### User API (`/api/v1/users`)


| Method   | Path                      | Description                                  |
| -------- | ------------------------- | -------------------------------------------- |
| `GET`    | `/api/v1/users`           | List all users                               |
| `POST`   | `/api/v1/users`           | Create a user (server-generated `id`, `201`) |
| `GET`    | `/api/v1/users/{user_id}` | Get one user by UUID                         |
| `PATCH`  | `/api/v1/users/{user_id}` | Partial update                               |
| `PUT`    | `/api/v1/users/{user_id}` | Full replacement                             |
| `DELETE` | `/api/v1/users/{user_id}` | Delete user (`204`)                          |


Use **Try it out** in `/docs` to exercise the endpoints.

## Tests

Pydantic model tests live under `tests/` (e.g. `tests/test_user_model.py` for the `User` model).


| Action         | With venv                         | Without venv                             |
| -------------- | --------------------------------- | ---------------------------------------- |
| Run all tests  | `pytest`                          | `uv run pytest`                          |
| Run one file   | `pytest tests/test_user_model.py` | `uv run pytest tests/test_user_model.py` |
| Verbose output | `pytest -v`                       | `uv run pytest -v`                       |


Requires dev dependencies (`pytest`). Install them with `uv sync --dev` if you only ran `uv sync` before.

## Project layout

```
fastapi_store/
├── .venv/                  # created by uv sync (gitignored)
├── app/
│   └── models/users.py
├── tests/
│   └── test_user_model.py
├── main.py
├── pyproject.toml
└── uv.lock
```

