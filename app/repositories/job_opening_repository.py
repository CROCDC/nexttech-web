from app.models.job_opening import JobOpening
from app.factory import db

class JobOpeningRepository:

    @staticmethod
    def get_all():
        return JobOpening.query.all()

    @staticmethod
    def get_by_id(job_id):
        return JobOpening.query.get(job_id)

    @staticmethod
    def add(job_opening):
        db.session.add(job_opening)
        db.session.commit()

    @staticmethod
    def update():
        db.session.commit()

    @staticmethod
    def delete(job_opening):
        db.session.delete(job_opening)
        db.session.commit() 