from datetime import datetime
from flask import Flask
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
    
    @app.context_processor
    def inject_current_year():
        return {'current_year': datetime.now().year}

    # Inicializar extensiones
    db.init_app(app)
    migrate.init_app(app, db)

    @app.context_processor
    def inject_current_year():
        return {'current_year': datetime.now().year}

    with app.app_context():
        from app.routes import register_routes
        register_routes(app)
        db.create_all()
    
    return app 