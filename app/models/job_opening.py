import enum

from app.factory import db


class JobTypeEnum(enum.Enum):
    DESIGNER = ('Designer', 'designer.png')
    SOFTWARE_ENGINEER = ('Software Engineer', 'software_engineer.png')
    AI = ('AI', 'ai.png')
    CYBERSECURITY = ('Cybersecurity', 'cybersecurity.png')

    def __init__(self, label, icon):
        self.label = label
        self.icon = icon


class JobOpening(db.Model):
    __tablename__ = 'job_openings'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    job_type = db.Column(db.Enum(JobTypeEnum), nullable=False)

    def __repr__(self):
        return f'<JobOpening {self.title}>'
