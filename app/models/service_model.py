from app import db
from uuid import uuid4
from datetime import datetime, timezone
from sqlalchemy import Float

class Service(db.Model):
    service_id = db.Column(db.String(255), primary_key=True, default=lambda:str(uuid4()))
    branch_id = db.Column(db.String(255), db.ForeignKey("branch.branch_id"), nullable=True)
    service_name = db.Column(db.String(255), nullable=False)
    original_price = db.Column(Float, nullable=False)
    is_sale = db.Column(db.Boolean, nullable=False, default=False)
    discount_percentage = db.Column(Float, nullable=False, default=0.0)
    final_price = db.Column(Float, nullable=False, default=0.0)
    category = db.Column(db.String(255), nullable=False)
    image = db.Column(db.Text, nullable=False)
    average_rate = db.Column(Float, nullable=True, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    
    branch = db.relationship("Branch", backref="services")

    
    
    def to_dict(self):
        return {
            "service_id": self.service_id,
            "branch_id": self.branch_id,
            "branch":{
              "branch_name": self.branch.branch_name if self.branch_id else None
            },
            "service_name": self.service_name,
            "original_price": self.original_price,
            "final_price": self.final_price,
            "is_sale": self.is_sale,
            "discount_percentage": self.discount_percentage,
            "category": self.category,
            "image": self.image,
            "avarage_rate": self.average_rate,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None

        }

