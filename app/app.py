from flask import render_template, request, jsonify
from app import app, db
from app.models.contact import ContactMessage
from app.repositories.contact_repository import ContactMessageRepository

# Crear las tablas
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True) 