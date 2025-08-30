from ..extension import db
from datetime import datetime, timezone
from ..helper.functions import generate_id


class Owner(db.Model):
    owner_id = db.Column(db.String(255), primary_key=True, default=lambda:generate_id("OWNER"))
    account_id = db.Column(db.String(255), db.ForeignKey("auth.account_id"), nullable=False)
    first_name = db.Column(db.String(255) )
    last_name = db.Column(db.String(255) )
    middle_initial = db.Column(db.String(255))
    phone_number = db.Column(db.Integer)
    birthday = db.Column("birthday", db.DateTime)
    image = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    
    auth = db.relationship("Auth", backref="owners")
    
    
    def to_dict(self):
        return {
            "owner_id": self.owner_id,
            "account_id": self.account_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "middle_name": self.middle_initial,
            "birthday": self.birthday.isoformat() if self.birthday else None,
            "image": self.image,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

    