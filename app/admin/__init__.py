from flask import Blueprint

# Templates live in app/templates/admin/, served from the app's template folder.
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

from app.admin import routes  # noqa: E402,F401  (registers the routes on import)
