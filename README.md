# FastAPI Store [Work in progress]

> **Learning project** — FastAPI e-commerce backend built step by step, without a database (in-memory store). Each iteration introduces a new FastAPI pattern.

A **FastAPI** e-commerce backend project. Data is stored in memory (no database yet), focused on learning FastAPI patterns:

- Pydantic schemas per use case (`User`, `CreateUser`, `UpdateUser`, `UserReplace`, same for `Product`)
- REST conventions: `POST` (create), `GET` (list & detail), `PATCH` (partial update), `PUT` (full replace), `DELETE`
- UUIDs in URL paths, `Decimal` for prices, soft delete on products
- `APIRouter` per domain — equivalent of Django's `include()` in `urls.py`
- OpenAPI documentation with grouped routes (`tags`) and documented `404` responses

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
| `DELETE` | `/api/v1/users/{user_id}` | Hard delete (`204`)                          |

### Product API (`/api/v1/products`)

| Method   | Path                            | Description                                      |
| -------- | ------------------------------- | ------------------------------------------------ |
| `GET`    | `/api/v1/products`              | List all products (`?active_only=true` to filter)|
| `POST`   | `/api/v1/products`              | Create a product (`201`)                         |
| `GET`    | `/api/v1/products/{product_id}` | Get one product by UUID                          |
| `PATCH`  | `/api/v1/products/{product_id}` | Partial update (use to deactivate)               |
| `PUT`    | `/api/v1/products/{product_id}` | Full replacement                                 |
| `DELETE` | `/api/v1/products/{product_id}` | Soft delete — sets `is_active=false` (`204`)     |


Use **Try it out** in `/docs` to exercise the endpoints.

## Tests

Pydantic model tests live under `tests/`.

| File | Covers |
| ---- | ------ |
| `tests/test_user_model.py` | `User` model — unit |
| `tests/test_product_model.py` | `Product` model — unit |
| `tests/test_users_router.py` | User routes — integration |
| `tests/test_products_router.py` | Product routes — integration |


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
│   ├── models/
│   │   ├── users.py        # User, CreateUser, UpdateUser, UserReplace
│   │   └── products.py     # Product, CreateProduct, UpdateProduct, ProductReplace
│   └── routers/
│       ├── users.py        # CRUD /api/v1/users
│       └── products.py     # CRUD /api/v1/products (soft delete)
├── tests/
│   ├── test_user_model.py
│   ├── test_product_model.py
│   ├── test_users_router.py
│   └── test_products_router.py
├── main.py                 # app entry point — mounts routers only
├── pyproject.toml
└── uv.lock
```

## Roadmap

### Done
- [X] `User` — full CRUD, unit + integration tests
- [X] `Product` — full CRUD, soft delete, `?active_only` filter, unit + integration tests
- [X] `APIRouter` per domain, `Decimal` for prices
- [X] In-memory store with test isolation (pytest fixtures)

### Next
- [ ] **Cart** — add/remove items, link to User and Product (UUID references)
- [ ] **Order** — place order from cart, stock check, price snapshot, order status
- [ ] **Service layer** — cross-domain business logic (stock management, order lifecycle)
- [ ] **`Depends()`** — FastAPI dependency injection (shared resource lookups, future auth)

### Later
- [ ] **Database** — replace in-memory store with SQLAlchemy + Alembic migrations
- [ ] **Authentication** — JWT-based auth, `get_current_user` dependency
- [ ] **Pagination** — query params (`limit`, `offset`) on list endpoints
