from app import db
from uuid import uuid4
from datetime import datetime, timezone
from sqlalchemy import Float

class Service(db.Model):
    service_id = db.Column(db.String(255), primary_key=True, default=lambda:str(uuid4()))
    branch_id = db.Column(db.String(255), db.ForeignKey("branch.branch_id"), nullable=False)
    service_name = db.Column(db.String(255), nullable=False)
    price = db.Column(Float, nullable=False)
    category = db.Column(db.String(255), nullable=False)
    image = db.Column(db.Text, nullable=False)
    avarage_rate = db.Column(db.Float, nullable=True, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    
    branch = db.relationship("Branch", backref="services")

    
    def to_dict(self):
        return {
            "service_id": self.service_id,
            "branch_id": self.branch_id,
            "branch":{
              "branch_name": self.branch.branch_name
            },
            "service_name": self.service_name,
            "price": self.price,
            "category": self.category,
            "image": self.image,
            "avarage_rate": self.avarage_rate,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

