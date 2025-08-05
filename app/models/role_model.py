from app import db
from ..helper.constant import role_enum

class Role(db.Model):
    role_id = db.Column(db.String(255), primary_key=True, default="")
    role_name = db.Column(role_enum, nullable=False)
    
    def to_dict(self):
        return {
            "role_id": self.role_id,
            "role": self.role,
        }