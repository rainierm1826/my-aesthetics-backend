from app import db
from uuid import uuid4
from datetime import datetime, timezone

class Branch(db.Model):
    branch_id = db.Column(db.String(255), primary_key=True, default=lambda:str(uuid4()))
    address_id = db.Column(db.String(255), db.ForeignKey("address.address_id"))
    branch_name = db.Column(db.String(255), nullable=False)
    image = db.Column(db.String(255), nullable=False)
    avarage_rate = db.Column(db.Float, nullable=False, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    
    address = db.relationship("Address", backref="branches")
    
    def to_dict(self):
        return {
            "branch_id": self.branch_id,
            "branch_name": self.branch_name,
            "image": self.image,
            "avarage_rate": self.avarage_rate,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "address": {
                "address_id": self.address.address_id,
                "region": self.address.region,
                "province": self.address.province,
                "city": self.address.city,
                "barangay": self.address.barangay,
                "lot": self.address.lot,
                "created_at": self.address.created_at.isoformat(),
                "updated_at": self.address.updated_at.isoformat()
                } if self.address else None
            }

