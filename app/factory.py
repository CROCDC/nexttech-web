from datetime import datetime
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os

# Inicializar extensiones
db = SQLAlchemy()
migrate = Migrate()

from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__)
    
    # Configuración de la base de datos
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///nexttech.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Configuración de uploads
    app.config['UPLOAD_FOLDER'] = os.environ.get('UPLOAD_FOLDER') or os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance', 'uploads')
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Project icons live on the same durable volume as the uploads (not baked
    # into the image), so they survive rebuilds and can be added via the admin
    # API/form without a deploy. Legacy icons committed under
    # static/assets/projects/ keep working through project_icon_url()'s fallback.
    app.config['PROJECT_ICONS_FOLDER'] = os.path.join(app.config['UPLOAD_FOLDER'], 'projects')
    os.makedirs(app.config['PROJECT_ICONS_FOLDER'], exist_ok=True)

    # Analytics (Umami) - el Website ID es público y actúa de interruptor
    # (sin valor en dev => no se trackea). La URL del script es constante y va
    # hardcodeada en los templates.
    app.config['UMAMI_WEBSITE_ID'] = os.environ.get('UMAMI_WEBSITE_ID')

    # Admin: protegido por HTTP Basic Auth con credenciales de entorno. Sin
    # ADMIN_PASSWORD el panel queda deshabilitado (responde 503). SECRET_KEY
    # sólo se usa para los mensajes flash del panel.
    app.config['ADMIN_USER'] = os.environ.get('ADMIN_USER', 'admin')
    app.config['ADMIN_PASSWORD'] = os.environ.get('ADMIN_PASSWORD')
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
    # Tope de subida (CVs en PDF, íconos de proyectos): 16 MB.
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

    # Inicializar extensiones
    db.init_app(app)
    migrate.init_app(app, db)

    @app.context_processor
    def inject_current_year():
        return {'current_year': datetime.now().year}

    # --- Cacheo de estáticos -------------------------------------------------
    # Cache-busting automático por mtime: url_for('static', ...) agrega ?v=<mtime>,
    # así la URL cambia cuando cambia el archivo y el cache largo es seguro.
    @app.url_defaults
    def add_static_cache_bust(endpoint, values):
        if endpoint != 'static':
            return
        filename = values.get('filename')
        if not filename:
            return
        try:
            mtime = os.path.getmtime(os.path.join(app.static_folder, filename))
            values['v'] = int(mtime)
        except OSError:
            pass

    ONE_YEAR = 31536000   # 365 días
    ONE_WEEK = 604800     # 7 días

    @app.after_request
    def set_static_cache_headers(response):
        if request.path.startswith('/static/'):
            if request.args.get('v'):
                # URL versionada por mtime (assets propios vía url_for):
                # como la URL cambia al cambiar el archivo, es seguro cachear
                # "para siempre" e inmutable.
                response.headers['Cache-Control'] = f'public, max-age={ONE_YEAR}, immutable'
            else:
                # Sin versión (p.ej. el footer compartido y favicon.svg que otras
                # webs embeben con URL hardcodeada): TTL alto pero NO inmutable,
                # para que los cambios igual propaguen dentro de la semana.
                response.headers['Cache-Control'] = f'public, max-age={ONE_WEEK}'
        return response

    with app.app_context():
        from app.routes import register_routes
        from app.admin import admin_bp
        from app.seeds import seed_projects
        register_routes(app)
        app.register_blueprint(admin_bp)
        db.create_all()
        seed_projects()

    return app