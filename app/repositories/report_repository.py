import json
import os
import re
from dataclasses import dataclass
from typing import Optional

# Directorio de datos de reportes (cada reporte = una carpeta con meta.json + body.html).
# Los videos/imágenes de cada reporte van en app/static/reportes/<slug>/ y se referencian
# desde body.html con url_for('static', filename='reportes/<slug>/<archivo>').
REPORTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'reports')

# Slug seguro: minúsculas, números y guiones. Evita path traversal.
_SLUG_RE = re.compile(r'^[a-z0-9][a-z0-9-]*$')


@dataclass
class Report:
    slug: str
    title: str
    subtitle: str
    footer_note: str
    body: str  # fragmento HTML escrito por el autor del reporte (contenido confiable)
    og_description: str = ''  # descripción para el preview social (cae a subtitle si vacío)
    og_image: str = ''        # nombre del archivo OG dentro de static/reportes/<slug>/ (ej. "og.png"); '' si no hay


class ReportRepository:
    """Acceso de sólo lectura a los reportes web almacenados en disco."""

    @staticmethod
    def _is_valid_slug(slug: str) -> bool:
        return bool(_SLUG_RE.match(slug))

    @staticmethod
    def get_by_slug(slug: str) -> Optional[Report]:
        if not ReportRepository._is_valid_slug(slug):
            return None

        report_dir = os.path.join(REPORTS_DIR, slug)
        meta_path = os.path.join(report_dir, 'meta.json')
        body_path = os.path.join(report_dir, 'body.html')
        if not (os.path.isfile(meta_path) and os.path.isfile(body_path)):
            return None

        with open(meta_path, encoding='utf-8') as f:
            meta = json.load(f)
        with open(body_path, encoding='utf-8') as f:
            body = f.read()

        return Report(
            slug=slug,
            title=meta.get('title', 'Reporte'),
            subtitle=meta.get('subtitle', ''),
            footer_note=meta.get('footer_note', ''),
            body=body,
            og_description=meta.get('og_description', ''),
            og_image=ReportRepository._resolve_og_image(slug, meta.get('og_image')),
        )

    @staticmethod
    def _resolve_og_image(slug: str, override: Optional[str]) -> str:
        """Nombre del archivo OG (1200×630) dentro de static/reportes/<slug>/.

        Prioridad: el que indique meta.json (`og_image`), si no `og.png`, si no `og.jpg`.
        Devuelve '' si no hay ninguno (el template emite preview sin imagen).
        La imagen la genera scripts/make_og_image.py del skill generate-nexttech-report-web.
        """
        static_dir = os.path.join(os.path.dirname(REPORTS_DIR), 'static', 'reportes', slug)
        candidates = [override] if override else []
        candidates += ['og.png', 'og.jpg']
        for name in candidates:
            if name and os.path.isfile(os.path.join(static_dir, name)):
                return name
        return ''

    @staticmethod
    def get_all() -> list[Report]:
        if not os.path.isdir(REPORTS_DIR):
            return []
        reports: list[Report] = []
        for slug in sorted(os.listdir(REPORTS_DIR)):
            report = ReportRepository.get_by_slug(slug)
            if report is not None:
                reports.append(report)
        return reports
