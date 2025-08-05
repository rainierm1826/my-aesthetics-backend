from ..extension import db
from datetime import datetime, timezone
from sqlalchemy import CHAR
from ..helper.constant import sex_enum
from ..helper.functions import generate_id

class WalkIn(db.Model):
    walk_in_id = db.Column(db.String(255), primary_key=True, default=generate_id("MY"))
    first_name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255), nullable=False)
    middle_initial = db.Column(CHAR(1))
    phone_number = db.Column(db.String(255))
    sex = db.Column(sex_enum)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    
    
    def to_dict(self):
        return {
            "walk_in_id": self.walk_in_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "middle_initial": self.middle_initial,
            "phone_number": self.phone_number,
            "sex": self.sex,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
