# Retiring a project without leaving its hostname dead

When a project hosted under `*.nexttech.com.ar` is shut down, its hostname is
taken over by this app and every request to it is redirected (`302`) to a
closing page on the main site: `https://nexttech.com.ar/proyectos-finalizados/<slug>`.

## How it works

```
Browser ─→ Cloudflare (wildcard tunnel *.nexttech.com.ar) ─→ nginx-proxy
        ─→ nexttech-web (VIRTUAL_HOST includes the old hostname)
        ─→ before_request: Host is a retired project's → 302 to the closing page
```

- **Routing:** the Cloudflare tunnel already sends every `*.nexttech.com.ar`
  hostname to `nginx-proxy`, and the Cloudflare Origin cert is a wildcard (see
  `infra.pantech` → `docs/CLOUDFLARE_TUNNEL.md`, `docs/ORIGIN_CERTS.md`). Adding
  the hostname to this app's `VIRTUAL_HOST` is enough; no DNS/tunnel/cert change.
- **Registry:** `app/data/sunset_projects.json`, read by
  `SunsetProjectRepository` (`app/repositories/sunset_project_repository.py`).
- **Redirect:** `redirect_sunset_project_hosts` in `app/routes.py`. Any path and
  method on the old hostname goes to the closing page. `302` (not `301`) so
  browsers don't cache it and a project can come back.
- **Page:** `app/templates/sunset_project.html`, `noindex`. The wording is the
  same for every project, plain and generic ("Sitio dado de baja" / "Dimos de
  baja el sitio de <name> porque el proyecto no continuó."); only the name
  changes. No project images or logos.

## Registry entry

```json
{
  "slug": "nahati",
  "name": "Ñahatí",
  "hosts": ["nahati.nexttech.com.ar"]
}
```

- `slug`: URL segment of the closing page (lowercase, hyphens).
- `name`: shown in the closing sentence.
- `hosts`: every hostname the project used. Must also be in `VIRTUAL_HOST`.

## Checklist to retire a project

1. **PR in this repo:** add the registry entry and the hostname to
   `VIRTUAL_HOST` in `docker-compose.yml`. Check the page locally at
   `/proyectos-finalizados/<slug>` and the redirect with
   `curl -I -H "Host: <hostname>" http://127.0.0.1:7001/`.
2. **On the server, before merging:**
   - Disable the project's Jenkins job, or a push to its repo redeploys it.
   - Back up its database if it has one:
     `docker exec <project>-db pg_dump -U <user> <db> > <project>-YYYYMMDD.sql`.
   - Stop it: `docker compose -p <project> down` (no `-v`; keep the volume).
   > Order matters: if two containers declare the same `VIRTUAL_HOST`,
   > nginx-proxy round-robins between them.
3. **Merge the PR.** Jenkins redeploys this app with the new hostname. Expect a
   few minutes of `503` on the old hostname between steps 2 and 3.
4. **Verify:** `curl -I https://<hostname>/` and a deep path return `302` to the
   closing page; the page renders on mobile.
5. **Cleanup (later):** remove the project's Infisical secrets and Umami website
   if not needed; after ~30 days, `docker volume rm <project>_<volume>` and its
   images. Remove it from the admin projects list if it is there.

Projects on their **own domain** (not `*.nexttech.com.ar`) need extra work: the
domain must be routed to the tunnel in Cloudflare and have a cert on
`nginx-proxy`. The redirect/page part is the same.

## Retired projects

| Project | Hostnames | Retired |
|---|---|---|
| Ñahatí | `nahati.nexttech.com.ar` | 2026-11 |
