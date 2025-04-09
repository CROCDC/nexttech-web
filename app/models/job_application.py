from datetime import datetime
from app.factory import db

class JobApplication(db.Model):
    __tablename__ = 'job_applications'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    document_id = db.Column(db.String(20), nullable=False)
    cv_path = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, full_name, phone, document_id, cv_path, created_at=None):
        self.full_name = full_name
        self.phone = phone
        self.document_id = document_id
        self.cv_path = cv_path
        self.created_at = created_at or datetime.utcnow()

    def to_dict(self):
        return {
            'id': self.id,
            'full_name': self.full_name,
            'phone': self.phone,
            'document_id': self.document_id,
            'cv_path': self.cv_path,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            full_name=data['full_name'],
            phone=data['phone'],
            document_id=data['document_id'],
            cv_path=data['cv_path'],
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else None
        ) 