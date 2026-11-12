import json
import os
from dataclasses import dataclass
from functools import lru_cache
from typing import Any, Optional

# Registry of retired ("sunset") projects. Each entry keeps the project's old
# hostnames alive: requests to them are redirected to /proyectos-finalizados/<slug>,
# a page that explains the project was closed. The file only changes with a deploy
# (it is baked into the image), so it is read once and cached.
SUNSET_PROJECTS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'sunset_projects.json')


@dataclass(frozen=True)
class SunsetProject:
    slug: str
    name: str
    hosts: tuple[str, ...]
    summary: str  # one sentence on what the site was; the page adds the closing wording
    icon: str = ''  # filename under static/assets/sunset/; '' shows no icon


def normalize_host(host: str) -> str:
    """Lowercase host without port or trailing dot, so `Host` headers compare cleanly."""
    return host.strip().lower().split(':', 1)[0].rstrip('.')


@lru_cache(maxsize=1)
def _load() -> tuple[SunsetProject, ...]:
    if not os.path.isfile(SUNSET_PROJECTS_FILE):
        return ()
    with open(SUNSET_PROJECTS_FILE, encoding='utf-8') as f:
        raw: list[dict[str, Any]] = json.load(f)
    return tuple(
        SunsetProject(
            slug=str(item['slug']),
            name=str(item['name']),
            hosts=tuple(normalize_host(str(h)) for h in item.get('hosts', [])),
            summary=str(item.get('summary', '')),
            icon=str(item.get('icon', '')),
        )
        for item in raw
    )


class SunsetProjectRepository:
    """Read-only access to the retired projects registry."""

    @staticmethod
    def get_all() -> list[SunsetProject]:
        return list(_load())

    @staticmethod
    def get_by_slug(slug: str) -> Optional[SunsetProject]:
        return next((p for p in _load() if p.slug == slug), None)

    @staticmethod
    def get_by_host(host: str) -> Optional[SunsetProject]:
        wanted = normalize_host(host)
        return next((p for p in _load() if wanted in p.hosts), None)
