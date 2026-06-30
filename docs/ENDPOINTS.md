# HTTP Endpoints

Reference of every HTTP route the app exposes, so adding or consuming endpoints
is quick. Keep this in sync when routes change.

Source of truth:
- Public routes: [`app/routes.py`](../app/routes.py) (`register_routes(app)`).
- Admin panel: [`app/admin/routes.py`](../app/admin/routes.py) — a blueprint
  (`admin_bp`, prefix `/admin`) registered in [`app/factory.py`](../app/factory.py).
- `/metrics`: added by `PrometheusMetrics(app)` in [`run.py`](../run.py).

Conventions for *how* to add one (factory → routes → repository → model) live in
[`CONVENTIONS.md`](CONVENTIONS.md).

---

## Public

| Method | Path | Request | Description |
|---|---|---|---|
| GET | `/` | — | Home. Renders `index.html` with the featured projects (`ProjectRepository.get_featured()`). |
| GET | `/projects` | — | Full projects grid (`ProjectRepository.get_all()`, ordered by `sort_order`). |
| GET | `/work-with-us` | — | Open job listings page (`JobOpeningRepository.get_all()`). |
| GET | `/reportes/<slug>` | path: `slug` | Renders a web report from `app/reports/<slug>/`. `404` if the slug is unknown/invalid. Builds absolute Open Graph URLs. |
| GET | `/robots.txt` | — | Serves the static `robots.txt`. |
| GET | `/sitemap.xml` | — | Serves the static `sitemap.xml`. |
| POST | `/send-message` | JSON: `name`, `email`, `message` | Stores a contact message. Returns `{success, message, data}`. `500` on error. |
| POST | `/submit-application` | multipart/form-data: `full_name`, `phone`, `document_id`, `cv` (PDF) | Stores a job application + saves the CV to `UPLOAD_FOLDER`. Returns `{success, message}`. `400` if a field/file is missing or the file is not a PDF. |

## Metrics

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/metrics` | — | Prometheus metrics (request stats + custom memory/CPU gauges). Added by the exporter in `run.py`; scraped per `prometheus.yml`. |

## Admin

All `/admin/*` routes (including the JSON API) are guarded by HTTP **Basic Auth**
([`app/admin/auth.py`](../app/admin/auth.py)) via a blueprint `before_request`:

- Credentials: `ADMIN_USER` (default `admin`) and `ADMIN_PASSWORD` (env).
- No `ADMIN_PASSWORD` set → the whole panel returns **503** (closed, never silently public).
- Missing/wrong credentials → **401** with `WWW-Authenticate: Basic`.

### Dashboard

| Method | Path | Description |
|---|---|---|
| GET | `/admin/` | Dashboard with counts (job openings, projects, contacts, applications). |

### Open job searches (búsquedas)

| Method | Path | Request | Description |
|---|---|---|---|
| GET | `/admin/busquedas` | — | List job openings. |
| GET / POST | `/admin/busquedas/nueva` | form: `title`, `description`, `job_type` | Create a job opening. |
| GET / POST | `/admin/busquedas/<id>/editar` | form: `title`, `description`, `job_type` | Edit a job opening. `404` if not found. |
| POST | `/admin/busquedas/<id>/eliminar` | — | Delete a job opening. |

`job_type` must be a `JobTypeEnum` member name (`DESIGNER`, `SOFTWARE_ENGINEER`, `AI`, `CYBERSECURITY`).

### Projects (proyectos)

| Method | Path | Request | Description |
|---|---|---|---|
| GET | `/admin/proyectos` | — | List projects (drag to reorder, inline featured toggle). |
| GET / POST | `/admin/proyectos/nuevo` | form (see below) | Create a project. |
| GET / POST | `/admin/proyectos/<id>/editar` | form (see below) | Edit a project. `404` if not found. |
| POST | `/admin/proyectos/<id>/destacado` | — | Toggle the `featured` flag. Newly featured projects go to the end of the featured order. Returns `{ok, featured, featured_order}`. |
| POST | `/admin/proyectos/reordenar` | JSON: `{order: [id, ...]}` | Persist drag-and-drop order (sets `sort_order` by position). Returns `{ok, count}`. |
| POST | `/admin/proyectos/<id>/eliminar` | — | Delete a project. |
| GET | `/admin/api/projects` | — | JSON list of all projects (for scripts/CLI). |
| POST | `/admin/api/projects` | JSON: list, or `{projects: [...]}` | Bulk upsert keyed by `name`. Returns `{created, updated, errors, total}`. |

Project form / API fields — required: `name`, `url`, `icon`, `description`.
Optional: `short_description` (home blurb), `round_icon`, `featured`,
`work_in_progress`, `sort_order`, `featured_order`. The form also accepts an
uploaded `icon_file` (SVG/PNG/JPG/WEBP/GIF) saved to `static/assets/projects/`.

### Inquiries (consultas)

| Method | Path | Description |
|---|---|---|
| GET | `/admin/consultas` | List contact messages. |
| POST | `/admin/consultas/<id>/eliminar` | Delete a contact message. |

### Applications (postulaciones)

| Method | Path | Description |
|---|---|---|
| GET | `/admin/postulaciones` | List job applications (CVs). |
| GET | `/admin/postulaciones/<id>/cv` | Download the stored CV (`404` if the file is missing). |
| POST | `/admin/postulaciones/<id>/eliminar` | Delete an application (also removes the CV file, best-effort). |
