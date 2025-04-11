import os
from datetime import datetime

from flask import render_template, request, jsonify
from werkzeug.utils import secure_filename

from app.factory import db
from app.models import JobApplication
from app.repositories.contact_repository import ContactMessageRepository
from app.repositories.job_application_repository import JobApplicationRepository
from app.repositories.job_opening_repository import JobOpeningRepository
from app.models.job_opening import JobTypeEnum


def register_routes(app):
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

