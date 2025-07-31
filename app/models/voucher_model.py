from app import db
from datetime import datetime, timezone
from uuid import uuid4

class Voucher(db.Model):
    voucher_id = db.Column(db.String(255), primary_key=True, default=lambda:str(uuid4()))
    voucher_code = db.Column(db.String(255), nullable=False)
    discount_amount = db.Column(db.Float, nullable=False, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    expires_at = db.Column(db.DateTime, nullable=False)
    
    def to_dict(self):
        return {
            "voucher_id": self.voucher_id,
            "voucher_code": self.voucher_code,
            "discount_amount": self.discount_amount,
            "is_used": self.is_used,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "expires_at": self.expires_at.isoformat()
        }