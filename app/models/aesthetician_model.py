from app import db
from datetime import datetime, timezone
from sqlalchemy import CHAR
from ..helper.constant import sex_enum, experience_enum, availability_enum
from uuid import uuid4

class Aesthetician(db.Model):
    aesthetician_id = db.Column(db.String(255), primary_key=True, default=lambda:str(uuid4()))
    branch_id = db.Column(db.String(255), db.ForeignKey("branch.branch_id"), nullable=False)
    first_name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255), nullable=False)
    middle_initial = db.Column(CHAR(1))
    phone_number = db.Column(db.String(255))
    image = db.Column(db.Text, nullable=True)
    sex = db.Column(sex_enum, nullable=False)
    experience = db.Column(experience_enum, nullable=False)
    average_rate = db.Column(db.Float, nullable=True, default=0)
    availability = db.Column(availability_enum, nullable=False)
    isDeleted = db.Column(db.Boolean, default=False)
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
            "availability": self.availability,
            "average_rate": self.average_rate,
            "image": self.image,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }