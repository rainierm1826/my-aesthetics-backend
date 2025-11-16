from email.policy import default
from app import db
from datetime import datetime, timezone
from sqlalchemy import CHAR
from .base_mixin import SoftDeleteMixin
from ..helper.functions import generate_id

class User(db.Model, SoftDeleteMixin):
    user_id = db.Column(db.String(255), primary_key=True, default=lambda: generate_id("MY"))
    account_id = db.Column(db.String(255), db.ForeignKey("auth.account_id"), nullable=False)
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    middle_initial = db.Column(CHAR(1))
    phone_number = db.Column(db.String(255))
    birthday = db.Column("birthday", db.DateTime)
    image = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    isDeleted = db.Column(db.Boolean, default=False)

    auth = db.relationship("Auth", backref="users")
    
    @property
    def age(self):
        if not self.birthday:
            return None
        
        today = datetime.now(timezone.utc).date()
        birth_date = self.birthday.date()
        return today.year-birth_date.year-((today.month, today.day) < (birth_date.month, birth_date.day))
    
    
    def to_dict(self):
        return {
            "user_id": self.user_id,
            "account_id": self.account_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "middle_initial": self.middle_initial,
            "birthday": self.birthday.isoformat() if self.birthday else None,
            "age": self.age,
            "image": self.image,
            "phone_number":self.phone_number,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    