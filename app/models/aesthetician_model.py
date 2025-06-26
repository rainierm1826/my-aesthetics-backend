from app import db
from uuid import uuid4
from datetime import datetime, timezone
from sqlalchemy import CHAR, Enum
from .base_model import sex_enum

class Aesthetician(db.Model):
    aesthetician_id = db.Column(db.String(255), primary_key=True, default=lambda:str(uuid4()))
    branch_id = db.Column(db.String(255), db.ForeignKey("branch.branch_id"), nullable=False)
    first_name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255), nullable=False)
    middle_initial = db.Column(CHAR(1))
    phone_number = db.Column(db.String(255))
    image = db.Column(db.String(255), nullable=False)
    sex = db.Column(sex_enum)
    experience = db.Column(Enum("pro", "regular", name="experience_enum"))
    avarage_rate = db.Column(db.Float, nullable=False, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    
    branch = db.relationship("Branch", backref="aestheticians")
    
    def to_dict(self):
        return {
            "aesthetician_id": self.aesthetician_id,
            "branch":{
                "branch_id": self.branch.branch_id,
                "branch_name": self.branch.branch_name,
            },
            "first_name": self.first_name,
            "last_name": self.last_name,
            "middle_initial": self.middle_initial,
            "phone_number": self.phone_number,
            "sex": self.sex,
            "experience": self.experience,
            "avarage_rate": self.avarage_rate,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }