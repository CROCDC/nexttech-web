from datetime import datetime
from app.models.contact import ContactMessage
from app import db

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