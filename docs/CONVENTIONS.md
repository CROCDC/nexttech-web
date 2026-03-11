# Flask Project Structure Conventions

This document describes the standard structure and patterns used in this Flask application. Use it as a blueprint for new Flask projects so they stay consistent and maintainable.

**Quick reference — request flow:**  
`run.py` → `app` (from `app.factory.create_app()`) → `register_routes(app)` → route handler → **Repository** → **Model** + `db` → response.

---

## 1. Root Layout

```
project/
├── app/                    # Application package (single source of truth)
├── migrations/             # Alembic/Flask-Migrate database migrations
├── scripts/                # One-off or dev/debug scripts (e.g. local-docker-debug.sh)
├── .github/workflows/      # GitHub Actions (e.g. deploy trigger)
├── docs/                   # Project documentation (e.g. this file)
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── run.py                  # Entry point (Flask app + optional metrics)
├── Jenkinsfile             # CI/CD pipeline (optional)
├── prometheus.yml          # Prometheus scrape config (optional)
├── .env                    # Local env (gitignored)
├── .dockerignore
└── .gitignore
```

- **No** `README.md` requirement at root; if present, keep it short and link to `docs/` for details.
- **Config** comes from environment variables; no config modules with secrets.

---

## 2. Application Package (`app/`)

### 2.1 Files at package root

| File          | Role |
|---------------|------|
| `__init__.py` | Imports `create_app` from `factory` and exposes `app = create_app()`. Kept minimal. |
| `factory.py`  | Application factory: creates `Flask` instance, config, extensions, registers routes, runs `db.create_all()` in context. |
| `routes.py`   | All HTTP routes. Defines a single function `register_routes(app)` that receives the app and registers blueprints or `@app.route` handlers. |

### 2.2 Subpackages

```
app/
├── __init__.py
├── factory.py
├── routes.py
├── models/           # SQLAlchemy models only
├── repositories/     # Data access layer (one per aggregate/entity)
├── templates/        # Jinja2 HTML templates
└── static/           # CSS, JS, images, robots.txt, sitemap.xml, manifest.json
```

- **No** `views/` or `controllers/`; route handlers live in `routes.py` (or in blueprints under a `blueprints/` package if the app grows).
- **No** business logic in `routes.py` beyond request/response handling; use repositories and (if needed) a thin service layer.

---

## 3. Application Factory (`app/factory.py`)

- Create the `Flask` app with `Flask(__name__)`.
- Load environment with `python-dotenv` (e.g. `load_dotenv()` at top of factory or early in bootstrap).
- Configure via `app.config` using `os.environ.get()` (e.g. `DATABASE_URL`, `UPLOAD_FOLDER`), with sensible defaults for local dev (e.g. SQLite).
- Initialize extensions **outside** `create_app` so they can be imported by models and repositories:
  - `db = SQLAlchemy()`
  - `migrate = Migrate()`
- Inside `create_app`:
  - Set config values.
  - Call `db.init_app(app)` and `migrate.init_app(app, db)`.
  - Optionally add `@app.context_processor` for global template variables (e.g. `current_year`).
  - Use `with app.app_context():` to:
    - Import and call `register_routes(app)`.
    - Run `db.create_all()` if you want schema creation on startup (typical for small apps; otherwise rely on migrations only).
  - Return `app`.

Dependencies (DB, Migrate) are initialized in the factory and imported elsewhere from `app.factory` (e.g. `from app.factory import db`).

---

## 4. Models (`app/models/`)

- One file per domain entity (e.g. `contact.py`, `job_opening.py`, `job_application.py`).
- `app/models/__init__.py` re-exports all models so the rest of the app can do `from app.models import ContactMessage, JobApplication, JobOpening`.
- Each model:
  - Imports `db` from `app.factory`.
  - Subclasses `db.Model`.
  - Uses `__tablename__` when the table name should differ from the default (e.g. `job_openings`, `job_applications`).
  - Defines columns with explicit types and `nullable` where relevant.
  - Optionally provides `to_dict()` (and if needed `from_dict()`) for JSON/serialization.
  - Enums (e.g. job type) can live in the same file as the model that uses them or in a dedicated `enums.py`.

Do **not** put queries or persistence logic in models; that belongs in repositories.

---

## 5. Repositories (`app/repositories/`)

- One module per aggregate/entity (e.g. `contact_repository.py`, `job_opening_repository.py`, `job_application_repository.py`).
- Each repository is a class with **static methods** (or a single instance if you prefer dependency injection later).
- Responsibilities:
  - Run queries (e.g. `Model.query.all()`, `Model.query.get(id)`).
  - Add/update/delete via `db.session.add`, `db.session.commit()`, `db.session.rollback()`.
  - Encapsulate validation and file-handling rules (e.g. allowed file types, unique filenames) when they are part of “saving” an entity.
- Routes call repositories, not raw `db.session` or model queries (except trivial one-off cases if you document them).
- Repositories import models from `app.models` and `db` from `app.factory`. They do **not** import Flask `request` or `app`; the route layer passes in plain data (e.g. name, email, message or form data).

Naming: `XxxRepository` with methods like `get_all`, `get_by_id`, `save`, `create_xxx`, etc.

---

## 6. Routes (`app/routes.py`)

- Single public function: `register_routes(app)`.
- All route decorators use `@app.route(...)` inside this function.
- Handlers:
  - Parse request (JSON, form, files).
  - Validate required fields and return 400 with a clear message when invalid.
  - Call one or more repositories (or services) with plain Python data.
  - Return `render_template(...)` for pages or `jsonify(...)` for APIs, with appropriate status codes.
- On persistence errors, call `db.session.rollback()` and return 500 with a safe message; do not leak internal exceptions.
- File uploads: use `werkzeug.utils.secure_filename` and a dedicated `UPLOAD_FOLDER` from config; generate unique filenames (e.g. timestamp + original name) to avoid collisions. Prefer moving file logic into a repository method when it’s part of creating an entity (e.g. `JobApplicationRepository.create_job_application(...)`).

Static files like `robots.txt` and `sitemap.xml` can be served with `send_from_directory(app.static_folder, '...')`.

---

## 7. Static Files and Templates

- **Templates:** `app/templates/`. One template per main page (e.g. `index.html`, `projects.html`, `work_with_us.html`). Use Jinja2; global variables (e.g. `current_year`) come from context processors in the factory.
- **Static:** `app/static/`. Organize as:
  - `static/css/` — stylesheets.
  - `static/js/` — scripts.
  - `static/assets/` — images, favicons, OG images.
  - Root of `static/`: `robots.txt`, `sitemap.xml`, `manifest.json` if needed.

Reference static files with `url_for('static', filename='...')` in templates.

---

## 8. Database and Migrations

- **ORM:** Flask-SQLAlchemy with a single `db` instance from `app.factory`.
- **Migrations:** Flask-Migrate (Alembic). Migrations live under `migrations/` with:
  - `env.py` — uses the app’s `db` and Flask app context so that `target_metadata` comes from `db` (no need to import models manually if metadata is bound to the same `db`).
  - `alembic.ini` — standard Alembic config.
  - `script.py.mako` — template for revision files.
  - `versions/` — revision scripts (e.g. `xxx_add_job_applications.py`).
- **Database URL:** From environment (`DATABASE_URL`). Default in code can be SQLite for local dev; production uses PostgreSQL (or similar) via env.
- After schema changes, run `flask db migrate` and `flask db upgrade` (or equivalent in Docker/CI). For autogenerate to detect new models, they must be imported when the app loads (e.g. via `app.models` or routes/repositories); ensure `FLASK_APP` is set so `flask db migrate` runs with a loadable app.

---

## 9. Entry Point and Observability

- **Entry point:** `run.py` at project root.
  - Imports the app from `app` (e.g. `from app import app`).
  - Can attach Prometheus metrics (e.g. `prometheus_flask_exporter`) and custom gauges (e.g. memory, CPU).
  - Runs with `app.run(host='0.0.0.0', port=7001, debug=True)` for local dev; production uses `flask run` or a WSGI server (e.g. Gunicorn) with host/port from env.
- **Metrics:** Expose a `/metrics` endpoint for Prometheus; configure `prometheus.yml` to scrape it (and optionally postgres-exporter, etc.). Keep metrics registration in one place (e.g. `run.py` or a small `metrics.py`).

---

## 10. Docker and Environment

- **Dockerfile:**
  - Base image: e.g. `python:3.9-slim`.
  - Install only system deps needed for Python packages (e.g. `gcc`, `python3-dev` for some wheels).
  - `COPY requirements.txt` then `pip install -r requirements.txt`, then `COPY . .`.
  - Set `FLASK_APP=run.py` (or the module that exposes `app`).
  - Create any required dirs (e.g. uploads) and set permissions.
  - Expose the app port (e.g. 7001). Default command: `flask run --host=0.0.0.0 --port=7001`.
- **docker-compose.yml:**
  - Service `web`: build from Dockerfile, env vars for `DATABASE_URL`, `UPLOAD_FOLDER`, etc., depends on DB with healthcheck, volumes for uploads and (if needed) code.
  - Service `db`: PostgreSQL with healthcheck, persistent volume.
  - Optional: `postgres-exporter`, `prometheus` for observability.
  - Use external network (e.g. `proxy`) if the app sits behind a reverse proxy.
- **Environment:** All secrets and environment-specific values (DB URL, upload path, debug, host, port) come from environment variables. Use `.env` locally (gitignored) and inject env in Docker/CI.

---

## 11. CI/CD

- **GitHub Actions:** Optional workflow under `.github/workflows/` (e.g. `deploy.yml`) that runs on push to `main` and triggers an external deploy (e.g. Jenkins) via secrets; no secrets in the repo.
- **Jenkins:** Optional `Jenkinsfile` that builds with `docker compose`, supports `FORCE_REBUILD` / `FULL_CLEAN` from commit message, and runs `docker compose up -d`. Keeps deploy steps in one place.

---

## 12. Code Conventions

Code in this project is **strongly typed**. Prefer clarity and tooling support over brevity.

- **Type hints (mandatory):**
  - Annotate all function and method parameters and return types.
  - Use the `typing` module: `Optional[T]`, `List[T]`, `Dict[K, V]`, `Tuple[...]`, etc. Use `list[...]`, `dict[...]` (PEP 585) when the codebase is Python 3.9+.
  - Prefer concrete types; avoid `Any` unless integrating with untyped libraries or dynamic data. Use `cast()` or narrow types when you know more than the type checker.
- **Repository methods:** Signatures must be typed (e.g. `def get_by_id(self, job_id: int) -> Optional[JobOpening]:`). Return types for queries: single entity → `Optional[Model]`, collection → `list[Model]`.
- **Route handlers:** Request/response handling can use Flask types (`Response`, `tuple[str, int]`) where helpful; at least type the repository or service calls.
- **Models:** Attributes are inferred from SQLAlchemy; add `ClassVar` or type comments for non-column attributes if needed. `to_dict()` should return `dict[str, Any]` or a typed `TypedDict` for stricter contracts.
- **Static checking:** Run a type checker (e.g. `mypy` or `pyright`) in CI; fix or explicitly ignore only where necessary. Aim for strict or close-to-strict settings.
- **New code:** All new functions, methods, and public APIs must have type hints. When touching existing code, add or fix annotations as part of the change.

---

## 13. Naming and Style

- **Python:** PEP 8. All comments and docstrings in English.
- **Repositories:** `snake_case` filenames, e.g. `job_application_repository.py`; class name `JobApplicationRepository`.
- **Models:** `snake_case` filenames, e.g. `job_application.py`; class name `JobApplication`. Table names: `snake_case` plural when explicit (`__tablename__`).
- **Routes:** Function names descriptive of the action (e.g. `index`, `send_message`, `submit_application`). URL paths: kebab-case or simple (e.g. `/work-with-us`, `/send-message`).
- **Docs:** All documentation (including this file) in English.

---

## 14. Checklist for New Projects

When starting a new Flask project from this convention:

- [ ] Create `app/` with `__init__.py`, `factory.py`, `routes.py`.
- [ ] Add `app/models/` and `app/models/__init__.py`; one model file per entity; re-export in `__init__.py`.
- [ ] Add `app/repositories/`; one repository per entity; use static methods and keep routes thin.
- [ ] Register all routes inside `register_routes(app)` in `app/routes.py`.
- [ ] Put templates in `app/templates/`, static files in `app/static/` (css, js, assets).
- [ ] Use Flask-Migrate; keep `migrations/env.py` using app’s `db` and metadata.
- [ ] Entry point `run.py` imports app and runs it (and optional metrics).
- [ ] Config from env only; `.env` gitignored; Docker and CI inject env.
- [ ] Dockerfile and docker-compose.yml for local and deploy; healthchecks for DB.
- [ ] Optional: Prometheus metrics and `prometheus.yml`; optional Jenkins/GitHub Actions for deploy.
- [ ] No business logic in routes; no persistence logic in models; repositories own data access.
- [ ] All new code is strongly typed: type hints on parameters and return types; run mypy/pyright in CI.

---

This layout keeps the app testable, scalable, and easy to onboard. New team members can rely on `docs/CONVENTIONS.md` to understand and replicate the structure in other Flask projects.
