from app import db
from datetime import datetime, timezone, time
from ..helper.constant import branch_status_enum
from uuid import uuid4
from .base_mixin import SoftDeleteMixin

class Branch(db.Model, SoftDeleteMixin):
    branch_id = db.Column(db.String(255), primary_key=True, default=lambda:str(uuid4()))
    address_id = db.Column(db.String(255), db.ForeignKey("address.address_id"))
    branch_name = db.Column(db.String(255), nullable=False)
    image = db.Column(db.Text, nullable=True)
    average_rate = db.Column(db.Float, nullable=True, default=None)
    slot_capacity = db.Column(db.Integer, nullable=False, default=1)
    opening_time = db.Column(db.Time, nullable=False, default=time(10, 0))
    closing_time = db.Column(db.Time, nullable=False, default=time(17, 0))
    status = db.Column(branch_status_enum, nullable=False, default="active")
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    isDeleted = db.Column(db.Boolean, default=False)

    address = db.relationship("Address", backref="branches")
    
    def to_dict(self):
        return {
            "branch_id": self.branch_id,
            "branch_name": self.branch_name,
            "image": self.image,
            "avarage_rate": self.average_rate,
            "slot_capacity": self.slot_capacity,
            "opening_time": self.opening_time.strftime("%H:%M") if self.opening_time else None,
            "closing_time": self.closing_time.strftime("%H:%M") if self.closing_time else None,
            "status": self.status,
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

