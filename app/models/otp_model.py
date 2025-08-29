from ..extension import db
from datetime import datetime, timezone
from ..helper.functions import generate_id

class OTP(db.Model):
    otp_id = db.Column(db.String(), primary_key=True, default=lambda:generate_id("OTP"))
    email = db.Column(db.String(), nullable=False)
    otp_code = db.Column(db.String(6), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    expires_at = db.Column(db.DateTime(timezone=True), nullable=False)
    is_used = db.Column(db.Boolean, default=False)
    
    
    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "otp_code": self.otp_code,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "is_used": self.is_used
        }
    
    