from app import db
from sqlalchemy import Enum

class Role(db.Model):
    role_id = db.Column(db.String(255), primary_key=True, default="")
    role_name = db.Column(Enum("admin", "customer", "owner", name="role_enum"))
    
    def to_dict(self):
        return {
            "role_id": self.role_id,
            "role": self.role,
        }