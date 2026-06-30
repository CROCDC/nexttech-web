import os
from datetime import datetime
from flask import render_template, request, jsonify, send_from_directory, abort, url_for
from werkzeug.utils import secure_filename

from app.factory import db
from app.models import JobApplication
from app.repositories.contact_repository import ContactMessageRepository
from app.repositories.job_application_repository import JobApplicationRepository
from app.repositories.job_opening_repository import JobOpeningRepository
from app.repositories.project_repository import ProjectRepository
from app.repositories.report_repository import ReportRepository
from app.models.job_opening import JobTypeEnum


def register_routes(app):
    def project_icon_url(icon):
        """URL for a project icon: from the durable volume when it lives there,
        else the bundled static asset (legacy icons committed in the image).
        Both paths get a ?v=<mtime> cache-buster so a fresh icon = a fresh URL."""
        if not icon:
            return ''
        stored = os.path.join(app.config['PROJECT_ICONS_FOLDER'], icon)
        if os.path.isfile(stored):
            return url_for('project_icon', filename=icon, v=int(os.path.getmtime(stored)))
        return url_for('static', filename=f'assets/projects/{icon}')

    app.add_template_global(project_icon_url, 'project_icon_url')

    @app.route('/media/projects/<path:filename>')
    def project_icon(filename):
        """Serve project icons from the durable uploads volume, falling back to
        the bundled static dir for the legacy committed icons."""
        safe = secure_filename(filename)
        if not safe:
            abort(404)
        stored_dir = app.config['PROJECT_ICONS_FOLDER']
        static_dir = os.path.join(app.static_folder, 'assets', 'projects')
        if os.path.isfile(os.path.join(stored_dir, safe)):
            response = send_from_directory(stored_dir, safe)
        elif os.path.isfile(os.path.join(static_dir, safe)):
            response = send_from_directory(static_dir, safe)
        else:
            abort(404)
        # A versioned URL (?v=<mtime>) is immutable; without it, a short TTL so
        # edits still propagate. Mirrors set_static_cache_headers for /static/.
        if request.args.get('v'):
            response.headers['Cache-Control'] = 'public, max-age=31536000, immutable'
        else:
            response.headers['Cache-Control'] = 'public, max-age=604800'
        return response

    @app.route('/')
    def index():
        return render_template('index.html', featured_projects=ProjectRepository.get_featured())

    @app.route('/robots.txt')
    def robots():
        return send_from_directory(app.static_folder, 'robots.txt')

    @app.route('/sitemap.xml')
    def sitemap():
        return send_from_directory(app.static_folder, 'sitemap.xml')

    @app.route('/send-message', methods=['POST'])
    def send_message():
        try:
            data = request.get_json()
            name = data.get('name')
            email = data.get('email')
            message = data.get('message')

            # Usar el repositorio para crear el mensaje
            new_message = ContactMessageRepository.create_contact_message(name, email, message)

            return jsonify({
                'success': True,
                'message': 'Message saved successfully',
                'data': new_message.to_dict()
            })
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'success': False,
                'message': str(e)
            }), 500

    @app.route('/projects')
    def projects():
        return render_template('projects.html', projects=ProjectRepository.get_all())

    @app.route('/reportes/<slug>')
    def report(slug):
        report = ReportRepository.get_by_slug(slug)
        if report is None:
            abort(404)
        # URLs absolutas para el preview de Open Graph (WhatsApp/Slack/etc.).
        # El dominio público es configurable por env (default: producción).
        base = os.environ.get('REPORT_PUBLIC_BASE_URL', 'https://nexttech.com.ar').rstrip('/')
        canonical_url = base + url_for('report', slug=report.slug)
        og_image_url = None
        og_image_type = None
        if report.og_image:
            # url_for('static', ...) agrega ?v=<mtime> => cache-bust que ayuda a
            # forzar el re-scrape cuando se regenera la imagen del reporte.
            og_image_url = base + url_for('static', filename=f'reportes/{report.slug}/{report.og_image}')
            og_image_type = 'image/jpeg' if report.og_image.lower().endswith(('.jpg', '.jpeg')) else 'image/png'
        return render_template(
            'report_web.html',
            report=report,
            canonical_url=canonical_url,
            og_image_url=og_image_url,
            og_image_type=og_image_type,
        )

    @app.route('/work-with-us')
    def work_with_us():
        job_openings = JobOpeningRepository.get_all()
        return render_template('work_with_us.html', job_openings=job_openings, JobTypeEnum=JobTypeEnum)


    @app.route('/submit-application', methods=['POST'])
    def submit_application():
        try:
            # Verificar que todos los campos requeridos estén presentes
            required_fields = ['full_name', 'phone', 'document_id']
            if not all(key in request.form for key in required_fields):
                return jsonify({
                    'success': False,
                    'message': 'Todos los campos son requeridos'
                }), 400

            # Verificar que se haya subido un archivo
            if 'cv' not in request.files:
                return jsonify({
                    'success': False,
                    'message': 'El CV es requerido'
                }), 400

            file = request.files['cv']
            if file.filename == '':
                return jsonify({
                    'success': False,
                    'message': 'No se seleccionó ningún archivo'
                }), 400

            # Validar el tipo de archivo
            if not file.filename.lower().endswith('.pdf'):
                return jsonify({
                    'success': False,
                    'message': 'El archivo debe ser un PDF'
                }), 400

            # Guardar el archivo
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            unique_filename = f"{timestamp}_{filename}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(file_path)

            try:
                # Crear la aplicación
                application = JobApplication(
                    full_name=request.form['full_name'],
                    phone=request.form['phone'],
                    document_id=request.form['document_id'],
                    cv_path=file_path,
                    created_at=datetime.now()
                )

                # Guardar en la base de datos
                repository = JobApplicationRepository()
                repository.save(application)
                db.session.commit()

                return jsonify({
                    'success': True,
                    'message': 'Aplicación enviada exitosamente'
                })
            except Exception as e:
                db.session.rollback()
                # Si hay un error, intentar eliminar el archivo subido
                try:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                except:
                    pass
                return jsonify({
                    'success': False,
                    'message': f'Error al guardar la aplicación: {str(e)}'
                }), 500

        except Exception as e:
            # Si hay un error, intentar eliminar el archivo subido
            try:
                if 'file_path' in locals() and os.path.exists(file_path):
                    os.remove(file_path)
            except:
                pass
            return jsonify({
                'success': False,
                'message': f'Error al procesar la aplicación: {str(e)}'
            }), 500

