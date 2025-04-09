import os
from werkzeug.utils import secure_filename
from app.factory import db
from app.models.job_application import JobApplication
from datetime import datetime

class JobApplicationRepository:
    ALLOWED_EXTENSIONS = {'pdf'}

    @staticmethod
    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in JobApplicationRepository.ALLOWED_EXTENSIONS

    @staticmethod
    def save(application):
        try:
            db.session.add(application)
            db.session.commit()
            return application
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Error al guardar la aplicación: {str(e)}")

    @staticmethod
    def get_all():
        try:
            return JobApplication.query.all()
        except Exception as e:
            raise Exception(f"Error al obtener las aplicaciones: {str(e)}")

    @staticmethod
    def get_by_id(application_id):
        try:
            return JobApplication.query.get(application_id)
        except Exception as e:
            raise Exception(f"Error al obtener la aplicación: {str(e)}")

    @staticmethod
    def create_job_application(full_name, phone, document_id, cv_file, upload_folder):
        try:
            if not cv_file or not JobApplicationRepository.allowed_file(cv_file.filename):
                raise ValueError('Archivo CV inválido. Solo se permiten archivos PDF.')

            # Asegurar que el directorio de uploads existe
            os.makedirs(upload_folder, exist_ok=True)

            # Generar un nombre único para el archivo
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{secure_filename(document_id)}_{timestamp}.pdf"
            file_path = os.path.join(upload_folder, filename)
            
            # Guardar el archivo
            cv_file.save(file_path)

            # Crear la aplicación en la base de datos
            application = JobApplication(
                full_name=full_name,
                phone=phone,
                document_id=document_id,
                cv_path=file_path,
                created_at=datetime.now()
            )

            return JobApplicationRepository.save(application)

        except Exception as e:
            # Si hay un error, intentar eliminar el archivo si se creó
            if 'file_path' in locals() and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except:
                    pass
            raise Exception(f"Error al crear la aplicación: {str(e)}") 