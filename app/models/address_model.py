from app import db
from datetime import datetime, timezone
from uuid import uuid4

class Address(db.Model):
    address_id = db.Column(db.String(255), primary_key=True, default=lambda:str(uuid4()))
    region = db.Column(db.String(255), nullable=False)
    province = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(255), nullable=False)
    barangay = db.Column(db.String(255), nullable=False)
    lot = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    
    def to_dict(self):
        return {
            "address_id": self.address_id,
            "region": self.region,
            "province": self.province,
            "city": self.city,
            "barangay": self.barangay,
            "lot": self.lot,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
