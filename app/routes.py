from flask import render_template, request, jsonify

from app import app, db
from app.repositories.contact_repository import ContactMessageRepository


@app.route('/')
def index():
    return render_template('index.html')


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
