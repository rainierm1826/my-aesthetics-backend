from app import db
from datetime import datetime, timezone
from ..helper.functions import generate_voucher_code
from ..helper.constant import discount_type_enum

class Voucher(db.Model):
    voucher_code = db.Column(db.String(255), primary_key=True, default=lambda:generate_voucher_code())
    discount_type = db.Column(discount_type_enum, nullable=False)
    discount_amount = db.Column(db.Float, nullable=False, default=0.0)
    minimum_spend = db.Column(db.Float, nullable=False, default=0.0)
    quantity = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    valid_from = db.Column(db.DateTime, nullable=False)
    valid_until = db.Column(db.DateTime, nullable=False)
    isDeleted = db.Column(db.Boolean, default=False)

    
    def to_dict(self):
        return {
            "voucher_code": self.voucher_code,
            "discount_amount": self.discount_amount,
            "quantity": self.quantity,
            "discount_type": self.discount_type,
            "minimum_spend": self.minimum_spend,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "valid_until": self.valid_until.isoformat(),
            "valid_from": self.valid_from.isoformat()
        }