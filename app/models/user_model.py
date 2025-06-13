from app import db
from uuid import uuid4
from datetime import datetime, timezone
from sqlalchemy import CHAR

class User(db.Model):
    user_id = db.Column(db.String(255), primary_key=True, default=lambda:str(uuid4()))
    account_id = db.Column(db.String(255), db.ForeignKey("auth.account_id"), nullable=False)
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    middle_initial = db.Column(CHAR(1))
    phone_number = db.Column(db.Integer)
    birthday = db.Column(db.DateTime)
    image = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    auth = db.relationship("Auth", backref="users")
    
    @property
    def get_age(self):
        today = datetime.now(timezone.utc).date()
        birth_date = self.birthday.date()
        return today.year-birth_date.year-((today.month, today.day) < (birth_date.month, birth_date.day))
    
    
    def to_dict(self):
        return {
            "user_id": self.user_id,
            "account_id": self.account_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "middle_name": self.middle_name,
            "birthday": self.birthday,
            "image": self.image,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    