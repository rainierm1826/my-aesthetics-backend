from app import db
from datetime import datetime, timezone
from ..helper.functions import generate_voucher_code

class Voucher(db.Model):
    voucher_code = db.Column(db.String(255), primary_key=True, default=generate_voucher_code)
    discount_amount = db.Column(db.Float, nullable=False, default=0.0)
    quantity = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    expires_at = db.Column(db.DateTime, nullable=False)
    
    def to_dict(self):
        return {
            "voucher_code": self.voucher_code,
            "discount_amount": self.discount_amount,
            "quantity": self.quantity,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "expires_at": self.expires_at.isoformat()
        }