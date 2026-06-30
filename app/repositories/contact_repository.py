from datetime import datetime
from app.models.contact import ContactMessage
from app.factory import db

class ContactMessageRepository:
    @staticmethod
    def create_contact_message(name: str, email: str, message: str) -> ContactMessage:
        new_message = ContactMessage(
            name=name,
            email=email,
            message=message
        )
        
        db.session.add(new_message)
        db.session.commit()

        return new_message

    @staticmethod
    def get_all():
        return ContactMessage.query.order_by(ContactMessage.created_at.desc()).all()

    @staticmethod
    def get_by_id(message_id):
        return ContactMessage.query.get(message_id)

    @staticmethod
    def delete(message):
        db.session.delete(message)
        db.session.commit()