import os
import re
import urllib.error
import urllib.request

from flask import (abort, current_app, flash, jsonify, redirect, render_template,
                   request, send_file, url_for)
from werkzeug.utils import secure_filename

from app.admin import admin_bp
from app.admin.auth import enforce_admin_auth
from app.factory import db
from app.models.job_opening import JobOpening, JobTypeEnum
from app.models.project import Project
from app.repositories.contact_repository import ContactMessageRepository
from app.repositories.job_application_repository import JobApplicationRepository
from app.repositories.job_opening_repository import JobOpeningRepository
from app.repositories.project_repository import ProjectRepository

# Icon formats accepted by the projects page (svg renders crisp; raster as fallback).
_ICON_EXTENSIONS = {'svg', 'png', 'jpg', 'jpeg', 'webp', 'gif'}
# Content-Type → extension for icons fetched via icon_url.
_ICON_CONTENT_TYPES = {
    'image/svg+xml': 'svg', 'image/png': 'png', 'image/jpeg': 'jpg',
    'image/webp': 'webp', 'image/gif': 'gif',
}
_MAX_ICON_BYTES = 5 * 1024 * 1024


@admin_bp.before_request
def _guard():
    return enforce_admin_auth()


def _projects_asset_dir():
    """Durable folder (on the uploads volume) where new icons are stored, so they
    survive image rebuilds. Legacy icons still live under static/assets/projects/."""
    return current_app.config['PROJECT_ICONS_FOLDER']


def _allowed_icon(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in _ICON_EXTENSIONS


def _save_icon(file_storage):
    """Persist an uploaded icon into the durable projects folder, return its name."""
    filename = secure_filename(file_storage.filename)
    if not _allowed_icon(filename):
        raise ValueError('Formato de ícono no permitido (usá SVG, PNG, JPG, WEBP o GIF).')
    os.makedirs(_projects_asset_dir(), exist_ok=True)
    file_storage.save(os.path.join(_projects_asset_dir(), filename))
    return filename


def _icon_name_from(project_name, ext):
    """Deterministic icon filename from the project name, so re-fetching a
    project's icon overwrites it instead of piling up files."""
    slug = re.sub(r'[^a-z0-9]+', '-', (project_name or '').lower()).strip('-') or 'project'
    return f'{slug}.{ext}'


def _download_icon(url, project_name):
    """Fetch an icon by URL (admin-only) into the durable folder, return its name."""
    if not re.match(r'^https?://', url, re.I):
        raise ValueError('icon_url debe ser una URL http(s).')
    req = urllib.request.Request(url, headers={'User-Agent': 'nexttech-web/1.0'})
    with urllib.request.urlopen(req, timeout=10) as resp:
        ctype = (resp.headers.get('Content-Type') or '').split(';')[0].strip().lower()
        data = resp.read(_MAX_ICON_BYTES + 1)
    if len(data) > _MAX_ICON_BYTES:
        raise ValueError('El ícono supera el tamaño máximo (5 MB).')
    ext = _ICON_CONTENT_TYPES.get(ctype)
    if ext is None:
        tail = url.split('?', 1)[0].rsplit('.', 1)
        candidate = tail[1].lower() if len(tail) == 2 else ''
        ext = candidate if candidate in _ICON_EXTENSIONS else None
    if ext is None:
        raise ValueError('No se pudo determinar el formato del ícono (SVG/PNG/JPG/WEBP/GIF).')
    os.makedirs(_projects_asset_dir(), exist_ok=True)
    with open(os.path.join(_projects_asset_dir(), _icon_name_from(project_name, ext)), 'wb') as fh:
        fh.write(data)
    return _icon_name_from(project_name, ext)


# --- Dashboard -------------------------------------------------------------

@admin_bp.route('/')
def dashboard():
    counts = {
        'job_openings': len(JobOpeningRepository.get_all()),
        'projects': ProjectRepository.count(),
        'contacts': len(ContactMessageRepository.get_all()),
        'applications': len(JobApplicationRepository.get_all()),
    }
    return render_template('admin/dashboard.html', counts=counts)


# --- Búsquedas abiertas (job openings) -------------------------------------

@admin_bp.route('/busquedas')
def job_openings():
    return render_template('admin/job_openings.html',
                           job_openings=JobOpeningRepository.get_all())


@admin_bp.route('/busquedas/nueva', methods=['GET', 'POST'])
@admin_bp.route('/busquedas/<int:opening_id>/editar', methods=['GET', 'POST'])
def job_opening_form(opening_id=None):
    opening = JobOpeningRepository.get_by_id(opening_id) if opening_id else None
    if opening_id and opening is None:
        abort(404)

    if request.method == 'POST':
        title = (request.form.get('title') or '').strip()
        description = (request.form.get('description') or '').strip()
        job_type_name = request.form.get('job_type')
        if not title or not description or job_type_name not in JobTypeEnum.__members__:
            flash('Completá título, descripción y tipo.', 'error')
        else:
            job_type = JobTypeEnum[job_type_name]
            if opening is None:
                JobOpeningRepository.add(JobOpening(
                    title=title, description=description, job_type=job_type))
                flash('Búsqueda creada.', 'success')
            else:
                opening.title = title
                opening.description = description
                opening.job_type = job_type
                JobOpeningRepository.update()
                flash('Búsqueda actualizada.', 'success')
            return redirect(url_for('admin.job_openings'))

    return render_template('admin/job_opening_form.html',
                           opening=opening, job_types=list(JobTypeEnum))


@admin_bp.route('/busquedas/<int:opening_id>/eliminar', methods=['POST'])
def job_opening_delete(opening_id):
    opening = JobOpeningRepository.get_by_id(opening_id)
    if opening is None:
        abort(404)
    JobOpeningRepository.delete(opening)
    flash('Búsqueda eliminada.', 'success')
    return redirect(url_for('admin.job_openings'))


# --- Proyectos -------------------------------------------------------------

@admin_bp.route('/proyectos')
def projects():
    return render_template('admin/projects.html',
                           projects=ProjectRepository.get_all())


@admin_bp.route('/proyectos/nuevo', methods=['GET', 'POST'])
@admin_bp.route('/proyectos/<int:project_id>/editar', methods=['GET', 'POST'])
def project_form(project_id=None):
    project = ProjectRepository.get_by_id(project_id) if project_id else None
    if project_id and project is None:
        abort(404)

    if request.method == 'POST':
        name = (request.form.get('name') or '').strip()
        url = (request.form.get('url') or '').strip()
        description = (request.form.get('description') or '').strip()
        short_description = (request.form.get('short_description') or '').strip()
        icon = (request.form.get('icon') or '').strip()
        round_icon = request.form.get('round_icon') == 'on'
        featured = request.form.get('featured') == 'on'
        work_in_progress = request.form.get('work_in_progress') == 'on'
        sort_order = request.form.get('sort_order', type=int) or 0
        featured_order = request.form.get('featured_order', type=int) or 0

        icon_url = (request.form.get('icon_url') or '').strip()
        upload = request.files.get('icon_file')
        try:
            if upload and upload.filename:
                icon = _save_icon(upload)
            elif icon_url:
                icon = _download_icon(icon_url, name)
        except (ValueError, urllib.error.URLError, OSError) as exc:
            flash(str(exc), 'error')
            return render_template('admin/project_form.html', project=project,
                                   form=request.form)

        if not name or not url or not description or not icon:
            flash('Completá nombre, URL, descripción e ícono.', 'error')
            return render_template('admin/project_form.html', project=project,
                                   form=request.form)

        if project is None:
            project = Project()
        project.name = name
        project.url = url
        project.description = description
        project.short_description = short_description
        project.icon = icon
        project.round_icon = round_icon
        project.featured = featured
        project.work_in_progress = work_in_progress
        project.sort_order = sort_order
        project.featured_order = featured_order

        if project.id is None:
            ProjectRepository.add(project)
            flash('Proyecto creado.', 'success')
        else:
            ProjectRepository.save()
            flash('Proyecto actualizado.', 'success')
        return redirect(url_for('admin.projects'))

    return render_template('admin/project_form.html', project=project, form=None)


# JSON API for bulk-loading projects from a script/CLI. Protected by the same
# Basic Auth as the rest of the panel (the before_request guard), so the caller
# must pass the admin user/password. Upsert is keyed by project name.
_PROJECT_BOOL_FIELDS = {'round_icon', 'featured', 'work_in_progress'}
_PROJECT_INT_FIELDS = {'sort_order', 'featured_order'}
_PROJECT_STR_FIELDS = {'name', 'url', 'icon', 'description', 'short_description'}
_PROJECT_REQUIRED = {'name', 'url', 'icon', 'description'}


@admin_bp.route('/api/projects', methods=['GET'])
def api_projects_list():
    return jsonify([
        {
            'id': p.id, 'name': p.name, 'url': p.url, 'icon': p.icon,
            'description': p.description, 'short_description': p.short_description,
            'round_icon': p.round_icon, 'featured': p.featured,
            'work_in_progress': p.work_in_progress,
            'sort_order': p.sort_order, 'featured_order': p.featured_order,
        }
        for p in ProjectRepository.get_all()
    ])


@admin_bp.route('/api/projects', methods=['POST'])
def api_projects_upsert():
    payload = request.get_json(silent=True)
    if payload is None:
        return jsonify({'error': 'Body JSON inválido o ausente.'}), 400
    items = payload.get('projects') if isinstance(payload, dict) else payload
    if not isinstance(items, list):
        return jsonify({'error': 'Se espera una lista de proyectos (o {"projects": [...]}).'}), 400

    created, updated, errors = [], [], []
    for i, item in enumerate(items):
        if not isinstance(item, dict):
            errors.append({'index': i, 'error': 'No es un objeto.'})
            continue
        # icon_url is resolved before validation because it populates `icon`
        # (downloaded to the durable folder). It needs a name for the filename.
        icon_url = str(item.get('icon_url') or '').strip()
        if icon_url:
            name_for_icon = str(item.get('name') or '').strip()
            if not name_for_icon:
                errors.append({'index': i, 'name': item.get('name'),
                               'error': 'icon_url requiere name.'})
                continue
            try:
                item['icon'] = _download_icon(icon_url, name_for_icon)
            except (ValueError, urllib.error.URLError, OSError) as exc:
                errors.append({'index': i, 'name': item.get('name'),
                               'error': f'icon_url: {exc}'})
                continue
        missing = [f for f in _PROJECT_REQUIRED if not str(item.get(f) or '').strip()]
        if missing:
            errors.append({'index': i, 'name': item.get('name'),
                           'error': f'Faltan campos: {", ".join(sorted(missing))}'})
            continue

        project = Project.query.filter_by(name=item['name'].strip()).first()
        is_new = project is None
        if is_new:
            project = Project()
        for f in _PROJECT_STR_FIELDS:
            if f in item:
                setattr(project, f, str(item[f]).strip())
        for f in _PROJECT_BOOL_FIELDS:
            if f in item:
                setattr(project, f, bool(item[f]))
        for f in _PROJECT_INT_FIELDS:
            if f in item:
                try:
                    setattr(project, f, int(item[f]))
                except (TypeError, ValueError):
                    setattr(project, f, 0)
        if is_new:
            db.session.add(project)
            created.append(project.name)
        else:
            updated.append(project.name)

    db.session.commit()
    return jsonify({'created': created, 'updated': updated, 'errors': errors,
                    'total': ProjectRepository.count()})


@admin_bp.route('/proyectos/reordenar', methods=['POST'])
def project_reorder():
    """Persist drag-and-drop order: assign sort_order by position in the list."""
    payload = request.get_json(silent=True) or {}
    order = payload.get('order')
    if not isinstance(order, list):
        return jsonify({'error': 'Se espera {"order": [ids...]}'}), 400
    for index, pid in enumerate(order):
        project = ProjectRepository.get_by_id(pid)
        if project is not None:
            project.sort_order = index
    db.session.commit()
    return jsonify({'ok': True, 'count': len(order)})


@admin_bp.route('/proyectos/<int:project_id>/destacado', methods=['POST'])
def project_toggle_featured(project_id):
    """Flip the featured flag from the list view (no need to open the form).

    Turning it on appends the project to the end of the featured order so it
    shows last on the home scroller until reordered.
    """
    project = ProjectRepository.get_by_id(project_id)
    if project is None:
        abort(404)
    project.featured = not project.featured
    if project.featured:
        project.featured_order = ProjectRepository.next_featured_order()
    ProjectRepository.save()
    return jsonify({'ok': True, 'featured': project.featured,
                    'featured_order': project.featured_order})


@admin_bp.route('/proyectos/<int:project_id>/eliminar', methods=['POST'])
def project_delete(project_id):
    project = ProjectRepository.get_by_id(project_id)
    if project is None:
        abort(404)
    ProjectRepository.delete(project)
    flash('Proyecto eliminado.', 'success')
    return redirect(url_for('admin.projects'))


# --- Consultas (contact messages) ------------------------------------------

@admin_bp.route('/consultas')
def contacts():
    return render_template('admin/contacts.html',
                           messages=ContactMessageRepository.get_all())


@admin_bp.route('/consultas/<int:message_id>/eliminar', methods=['POST'])
def contact_delete(message_id):
    message = ContactMessageRepository.get_by_id(message_id)
    if message is None:
        abort(404)
    ContactMessageRepository.delete(message)
    flash('Consulta eliminada.', 'success')
    return redirect(url_for('admin.contacts'))


# --- Postulaciones (CVs) ---------------------------------------------------

@admin_bp.route('/postulaciones')
def applications():
    return render_template('admin/applications.html',
                           applications=JobApplicationRepository.get_all())


@admin_bp.route('/postulaciones/<int:application_id>/cv')
def application_cv(application_id):
    application = JobApplicationRepository.get_by_id(application_id)
    if application is None or not application.cv_path or not os.path.isfile(application.cv_path):
        abort(404)
    download_name = f'CV_{secure_filename(application.full_name)}.pdf'
    return send_file(application.cv_path, as_attachment=True, download_name=download_name)


@admin_bp.route('/postulaciones/<int:application_id>/eliminar', methods=['POST'])
def application_delete(application_id):
    application = JobApplicationRepository.get_by_id(application_id)
    if application is None:
        abort(404)
    # Best-effort cleanup of the stored CV file.
    if application.cv_path and os.path.isfile(application.cv_path):
        try:
            os.remove(application.cv_path)
        except OSError:
            pass
    JobApplicationRepository.delete(application)
    flash('Postulación eliminada.', 'success')
    return redirect(url_for('admin.applications'))
